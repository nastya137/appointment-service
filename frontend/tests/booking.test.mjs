import { after, before, test } from 'node:test'
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { mkdir } from 'node:fs/promises'

const { chromium } = createRequire(import.meta.url)('playwright')
const baseUrl = process.env.TEST_BASE_URL || 'http://127.0.0.1:5173'
const future = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
const nextDay = new Date(Date.now() + 8 * 86400000).toISOString().slice(0, 10)
const specialists = [
  {
    id: 1,
    display_name: 'Анна Смирнова',
    description: 'Помогает находить баланс между работой и отдыхом.',
  },
  {
    id: 2,
    display_name: 'Михаил Волков',
    description: 'Индивидуальные консультации.',
  },
]
const services = [
  {
    id: 11,
    name: 'Индивидуальная консультация',
    description: 'Спокойный разговор о том, что важно для вас.',
    duration_minutes: 60,
    price: 2500,
    currency: 'RUB',
  },
  {
    id: 12,
    name: 'Знакомство со специалистом',
    description: null,
    duration_minutes: 30,
    price: 0,
    currency: 'RUB',
  },
]
let browser
before(async () => {
  browser = await chromium.launch({
    channel: process.env.TEST_BROWSER || undefined,
    headless: true,
  })
  await mkdir('test-results', { recursive: true })
})
after(async () => {
  await browser?.close()
})

async function setup(t, override) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1080 },
    timezoneId: 'Europe/Moscow',
  })
  const page = await context.newPage()
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  t.after(async () => {
    await context.close()
    assert.deepEqual(errors, [], 'No browser runtime errors')
  })
  await page.route('**/specialists', async (route) => {
    if (override && (await override(route, 'specialists'))) return
    await route.fulfill({ json: specialists })
  })
  await page.route('**/services/specialist/*', async (route) => {
    if (override && (await override(route, 'services'))) return
    await route.fulfill({
      json: route.request().url().endsWith('/2')
        ? [{ ...services[0], id: 21, name: 'Консультация Михаила' }]
        : services,
    })
  })
  await page.route('**/appointments/available-slots?*', async (route) => {
    if (override && (await override(route, 'slots'))) return
    const date = new URL(route.request().url()).searchParams.get('target_date')
    await route.fulfill({
      json: [9, 10, 11, 12, 14, 15, 16, 17].map((hour) => ({
        start_datetime: `${date}T${hour.toString().padStart(2, '0')}:00:00+00:00`,
        end_datetime: `${date}T${(hour + 1).toString().padStart(2, '0')}:00:00+00:00`,
      })),
    })
  })
  await page.route('**/appointments', async (route) => {
    if (override && (await override(route, 'submit'))) return
    await route.fulfill({ status: 201, json: { id: 101, status: 'pending' } })
  })
  await page.goto(baseUrl)
  await page
    .locator('#specialist option[value="1"]')
    .waitFor({ state: 'attached' })
  return page
}

async function choose(page) {
  await page.locator('#specialist').selectOption('1')
  await page.locator('#service').selectOption('11')
  await page.locator('#date').fill(future)
  await page.getByText('09:00', { exact: true }).click()
  await page.locator('#contact').fill('@demo_user')
}

test('required fields validate and do not submit; labels and initial state are usable', async (t) => {
  let posts = 0
  const page = await setup(t, async (_, kind) => {
    if (kind === 'submit') posts++
    return false
  })
  assert.equal(await page.locator('#service').isDisabled(), true)
  assert.equal(await page.locator('#date').isDisabled(), true)
  await page.getByRole('button', { name: 'Создать демозапись' }).click()
  assert.equal(await page.locator('[aria-invalid="true"]').count(), 4)
  await page.waitForFunction(() => document.activeElement?.id === 'specialist')
  assert.equal(posts, 0)
  await page.screenshot({ path: 'test-results/validation.png', fullPage: true })
})

test('changing specialist, service and date clears dependent selections without a pre-submit summary', async (t) => {
  const page = await setup(t)
  await choose(page)
  assert.equal(await page.locator('.summary-card').count(), 0)
  assert.equal(
    await page.getByRole('button', { name: 'Создать демозапись' }).count(),
    1,
  )
  assert.match(await page.locator('.service-meta').innerText(), /60 мин/)
  await page.locator('#date').fill(nextDay)
  assert.equal(await page.locator('input[name="time"]:checked').count(), 0)
  await page.getByText('10:00', { exact: true }).click()
  await page.locator('#service').selectOption('12')
  assert.equal(await page.locator('input[name="time"]:checked').count(), 0)
  await page.locator('#specialist').selectOption('2')
  assert.equal(await page.locator('#service').inputValue(), '')
  assert.equal(await page.locator('#date').inputValue(), '')
  assert.equal(await page.locator('input[name="time"]').count(), 0)
})

test('late service and slot responses cannot replace the latest selection', async (t) => {
  const page = await setup(t, async (route, kind) => {
    const url = route.request().url()
    if (kind === 'services' && url.endsWith('/1')) {
      await new Promise((resolve) => setTimeout(resolve, 600))
      await route.fulfill({ json: services }).catch(() => {})
      return true
    }
    if (kind === 'slots' && url.includes(future)) {
      await new Promise((resolve) => setTimeout(resolve, 600))
      await route
        .fulfill({
          json: [
            {
              start_datetime: `${future}T22:00:00Z`,
              end_datetime: `${future}T23:00:00Z`,
            },
          ],
        })
        .catch(() => {})
      return true
    }
    return false
  })
  await page.locator('#specialist').selectOption('1')
  await page.locator('#specialist').selectOption('2')
  await page.locator('#service').selectOption('21')
  await page.locator('#date').fill(future)
  await page.locator('#date').fill(nextDay)
  await page.getByText('09:00', { exact: true }).waitFor()
  await page.waitForTimeout(750)
  assert.equal(await page.locator('#service option[value="11"]').count(), 0)
  assert.equal(await page.getByText('22:00', { exact: true }).count(), 0)
  assert.equal(await page.locator('input[name="time"]').count(), 8)
})

test('phone payload matches selection and rapid submission sends once; success and restart work', async (t) => {
  const payloads = []
  const page = await setup(t, async (route, kind) => {
    if (kind !== 'submit') return false
    payloads.push(route.request().postDataJSON())
    await new Promise((resolve) => setTimeout(resolve, 350))
    await route.fulfill({ status: 201, json: { id: 123, status: 'pending' } })
    return true
  })
  await choose(page)
  await page.locator('#contact-type').selectOption('phone')
  assert.equal(await page.locator('#contact').inputValue(), '')
  await page.getByRole('button', { name: 'Заполнить примером' }).click()
  await page.locator('#booking-form').evaluate((form) => {
    form.requestSubmit()
    form.requestSubmit()
  })
  assert.equal(await page.locator('#contact').isDisabled(), true)
  await page.getByRole('heading', { name: 'Демозапись создана' }).waitFor()
  assert.equal(payloads.length, 1)
  assert.equal(payloads[0].contact_type, 'phone')
  assert.equal(payloads[0].contact_value, '+79990000000')
  assert.equal(payloads[0].service_id, 11)
  assert.equal(payloads[0].start_datetime, `${future}T09:00:00+00:00`)
  await page.screenshot({ path: 'test-results/success.png', fullPage: true })
  assert.equal(await page.locator('.summary-card').count(), 1)
  assert.match(await page.locator('.summary-total').innerText(), /2\s?500/)
  await page
    .getByRole('button', { name: 'Создать ещё одну демозапись' })
    .click()
  assert.equal(await page.locator('.summary-card').count(), 0)
  assert.equal(await page.locator('#contact').inputValue(), '')
  assert.equal(await page.locator('input[name="time"]:checked').count(), 0)
})

test('request errors can be retried; empty slots and server errors are explained', async (t) => {
  let serviceFailed = false
  const page = await setup(t, async (route, kind) => {
    if (kind === 'services' && !serviceFailed) {
      serviceFailed = true
      await route.fulfill({ status: 500, body: 'error' })
      return true
    }
    if (kind === 'slots' && route.request().url().includes(nextDay)) {
      await route.fulfill({ json: [] })
      return true
    }
    if (kind === 'submit') {
      await route.fulfill({ status: 500, body: 'Internal Server Error' })
      return true
    }
    return false
  })
  await page.locator('#specialist').selectOption('1')
  await page.getByRole('button', { name: 'Повторить загрузку' }).click()
  await page.locator('#service').selectOption('11')
  await page.locator('#date').fill(nextDay)
  await page.getByText('На эту дату свободного времени нет').waitFor()
  await page.locator('#date').fill(future)
  await page.getByText('09:00', { exact: true }).click()
  await page.locator('#contact').fill('@demo_user')
  await page.getByRole('button', { name: 'Создать демозапись' }).click()
  await page.locator('.submit-error').waitFor()
  assert.equal(await page.locator('#contact').inputValue(), '@demo_user')
  assert.equal(
    await page.getByRole('button', { name: 'Создать демозапись' }).isEnabled(),
    true,
  )
})

test('conflict reloads slots and clears time; contact validation blocks invalid Telegram data', async (t) => {
  let posts = 0
  const page = await setup(t, async (route, kind) => {
    if (kind !== 'submit') return false
    posts++
    await route.fulfill({ status: 409, json: { detail: 'Occupied' } })
    return true
  })
  await choose(page)
  await page.locator('#contact').fill('123')
  await page.getByRole('button', { name: 'Создать демозапись' }).click()
  await page.locator('#contact-error').waitFor()
  assert.equal(posts, 0)
  await page.locator('#contact').fill('demo_user')
  await page.getByRole('button', { name: 'Создать демозапись' }).click()
  await page.locator('.submit-error').waitFor()
  assert.match(
    await page.locator('.submit-error').innerText(),
    /время уже заняли/,
  )
  assert.equal(await page.locator('input[name="time"]:checked').count(), 0)
})

test('desktop, mobile and narrow screens have no horizontal overflow', async (t) => {
  const page = await setup(t)
  await choose(page)
  await page.screenshot({ path: 'test-results/desktop.png', fullPage: true })
  for (const width of [1440, 1024, 768, 740, 390, 320]) {
    await page.setViewportSize({ width, height: 900 })
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
      true,
      `No overflow at ${width}px`,
    )
  }
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({ path: 'test-results/mobile.png', fullPage: true })
})
