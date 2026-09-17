<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { Specialist } from './entities/specialist/model/types'
import type { Service } from './entities/service/model/types'
import type { AvailableSlot } from './entities/appointment/model/types'
import { ApiError, requestJson } from './shared/api'
import { useResource } from './shared/useResource'
import {
  formatDay,
  formatPrice,
  formatTime,
  normalizeContact,
  parseApiDate,
  validateContact,
} from './shared/booking'
import type { ContactType } from './shared/booking'
import './App.css'

type Field = 'specialist' | 'service' | 'date' | 'time' | 'contact'
type Appointment = { id: number; status: string }

const specialistId = ref('')
const serviceId = ref('')
const date = ref('')
const time = ref('')
const contactType = ref<ContactType>('telegram')
const contact = ref('')
const description = ref('')
const errors = ref<Partial<Record<Field, string>>>({})
const submitError = ref('')
const isSubmitting = ref(false)
const appointment = ref<Appointment | null>(null)
const formElement = ref<HTMLFormElement | null>(null)
const successElement = ref<HTMLElement | null>(null)
const now = ref(Date.now())
let submitting = false

const nowTimer = window.setInterval(() => { now.value = Date.now() }, 30000)
onBeforeUnmount(() => window.clearInterval(nowTimer))

const servicesPath = computed(() =>
  specialistId.value ? `/services/specialist/${specialistId.value}` : null,
)
const slotsPath = computed(() => {
  if (!specialistId.value || !serviceId.value || !date.value) return null
  const params = new URLSearchParams({
    specialist_id: specialistId.value,
    service_id: serviceId.value,
    target_date: date.value,
  })
  return `/appointments/available-slots?${params}`
})

const {
  data: specialists,
  error: specialistsError,
  loading: specialistsLoading,
  retry: retrySpecialists,
} = useResource<Specialist>('/specialists')
const {
  data: services,
  error: servicesError,
  loading: servicesLoading,
  retry: retryServices,
} = useResource<Service>(servicesPath)
const {
  data: slots,
  error: slotsError,
  loading: slotsLoading,
  retry: retrySlots,
} = useResource<AvailableSlot>(slotsPath)

const specialist = computed(() =>
  specialists.value.find((item) => String(item.id) === specialistId.value),
)
const service = computed(() =>
  services.value.find((item) => String(item.id) === serviceId.value),
)
const availableSlots = computed(() =>
  slots.value.filter(
    (slot) => parseApiDate(slot.start_datetime).getTime() > now.value,
  ),
)
const today = computed(() => new Date(now.value).toISOString().slice(0, 10))
const readyForSlots = computed(() =>
  Boolean(specialistId.value && serviceId.value && date.value),
)
const progress = computed(() =>
  time.value ? 3 : specialistId.value && serviceId.value ? 2 : 1,
)

watch(appointment, async (value) => {
  if (!value) return
  await nextTick()
  successElement.value?.focus()
})

function clearErrors(...fields: Field[]) {
  const next = { ...errors.value }
  fields.forEach((field) => delete next[field])
  errors.value = next
  submitError.value = ''
}

function handleSpecialistChange() {
  serviceId.value = ''
  date.value = ''
  time.value = ''
  clearErrors('specialist', 'service', 'date', 'time')
}

function handleServiceChange() {
  time.value = ''
  clearErrors('service', 'time')
}

function handleDateChange() {
  time.value = ''
  clearErrors('date', 'time')
}

function handleContactTypeChange() {
  contact.value = ''
  clearErrors('contact')
}

function selectTime(value: string) {
  time.value = value
  clearErrors('time')
}

function fillExampleContact() {
  contact.value = contactType.value === 'telegram'
    ? '@demo_user'
    : '+7 (999) 000-00-00'
  clearErrors('contact')
}

function retrySlotLoading() {
  time.value = ''
  retrySlots()
}

function resetBooking() {
  appointment.value = null
  time.value = ''
  contact.value = ''
  description.value = ''
  errors.value = {}
  retrySlots()
}

async function handleSubmit() {
  if (submitting || appointment.value) return
  const nextErrors: Partial<Record<Field, string>> = {}
  if (!specialist.value)
    nextErrors.specialist = 'Выберите специалиста из списка.'
  if (!service.value)
    nextErrors.service = 'Выберите услугу специалиста.'
  if (!date.value || date.value < new Date().toISOString().slice(0, 10))
    nextErrors.date = 'Выберите сегодняшнюю или будущую дату.'
  if (
    !time.value ||
    !slots.value.some(
      (slot) =>
        slot.start_datetime === time.value &&
        parseApiDate(time.value).getTime() > Date.now(),
    )
  ) {
    nextErrors.time = 'Выберите доступное время.'
  }
  const contactError = validateContact(contact.value, contactType.value)
  if (contactError) nextErrors.contact = contactError
  errors.value = nextErrors
  submitError.value = ''

  if (Object.keys(nextErrors).length) {
    await nextTick()
    formElement.value
      ?.querySelector<HTMLElement>('[aria-invalid="true"]:not(:disabled)')
      ?.focus()
    return
  }

  submitting = true
  isSubmitting.value = true
  try {
    appointment.value = await requestJson<Appointment>('/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(20000),
      body: JSON.stringify({
        // Existing backend test account; authentication is outside this change.
        user_id: 1,
        specialist_id: Number(specialistId.value),
        service_id: Number(serviceId.value),
        start_datetime: time.value,
        contact_type: contactType.value,
        contact_value: normalizeContact(contact.value, contactType.value),
        problem_description: description.value.trim() || null,
      }),
    })
  } catch (error) {
    if (error instanceof ApiError && error.status === 409) {
      time.value = ''
      retrySlots()
      submitError.value =
        'Это время уже заняли. Мы обновили список — выберите другой свободный слот.'
    } else if (error instanceof ApiError && error.status === 422) {
      submitError.value =
        'Сервер не принял данные. Проверьте поля формы и выбранное время.'
    } else if (error instanceof ApiError) {
      submitError.value =
        'Не удалось создать запись. Данные формы сохранены. Попробуйте ещё раз позже.'
    } else {
      submitError.value =
        'Не удалось получить ответ сервера. Запись могла сохраниться — проверьте её перед повторной отправкой.'
    }
  } finally {
    submitting = false
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="demo-banner">
    <span class="demo-badge">ДЕМО</span>
    <span>Учебный проект. Реальные консультации не проводятся.</span>
  </div>
  <header class="site-header page-width">
    <a class="brand" href="./" aria-label="Тише — на главную">
      <span class="brand-symbol" aria-hidden="true">✳</span>
      тише<span class="brand-dot">.</span>
    </a>
    <span class="brand-caption">Пространство для разговора</span>
    <a class="header-link" href="#how-it-works">
      Как это работает <span aria-hidden="true">↗</span>
    </a>
  </header>

  <main class="page-width">
    <section class="intro" aria-labelledby="page-title">
      <div>
        <p class="eyebrow"><span /> КОНСУЛЬТАЦИИ СО СПЕЦИАЛИСТОМ</p>
        <h1 id="page-title">Время для <em>себя.</em></h1>
        <p class="intro-text">
          Начните с простого шага. Выберите специалиста
          <br class="desktop-break"> и удобное время для спокойного разговора.
        </p>
      </div>
      <div class="intro-art" aria-hidden="true">
        <svg viewBox="0 0 230 160" fill="none">
          <circle cx="146" cy="65" r="40" fill="#DABDA8" />
          <path
            d="M25 148V86a61 61 0 0 1 122 0v62M42 148V86a44 44 0 0 1 88 0v62M59 148V86a27 27 0 0 1 54 0v62"
            stroke="#A1A892"
            stroke-width="2"
          />
          <path
            d="M165 146c-9-29 11-45 38-48-1 27-14 43-38 48Zm0 0c-24-5-37-19-36-42 22 2 37 17 36 42Z"
            fill="#768570"
          />
          <path d="M165 157V133" stroke="#768570" stroke-width="2" />
        </svg>
      </div>
    </section>

    <div class="booking-layout">
      <div class="booking-main">
        <section
          v-if="appointment"
          ref="successElement"
          class="success-card"
          tabindex="-1"
          aria-labelledby="success-title"
        >
          <span class="success-icon" aria-hidden="true">✓</span>
          <p class="eyebrow">ЗАПИСЬ № {{ appointment.id }}</p>
          <h2 id="success-title">Демозапись создана</h2>
          <p>Всё получилось. Детали вашего выбора — в сводке записи.</p>
          <span class="status-pill">
            {{ appointment.status === 'confirmed' ? 'Подтверждена' : 'Ожидает подтверждения' }}
          </span>
          <p class="success-note">
            Это учебная демонстрация. Реальная встреча не состоится.
          </p>
          <button class="primary-button" type="button" @click="resetBooking">
            Создать ещё одну демозапись <span aria-hidden="true">↗</span>
          </button>
        </section>

        <form
          v-else
          id="booking-form"
          ref="formElement"
          novalidate
          @submit.prevent="handleSubmit"
        >
          <fieldset class="form-fields" :disabled="isSubmitting">
            <legend class="sr-only">Запись на консультацию</legend>

            <section class="form-section">
              <div class="section-heading">
                <span class="section-number">01</span>
                <div>
                  <h2>Специалист и услуга</h2>
                  <p>Выберите, с кем и о чём хотите поговорить</p>
                </div>
              </div>
              <div class="field-grid">
                <div class="field">
                  <label for="specialist">
                    Специалист <span class="required-mark">*</span>
                  </label>
                  <select
                    id="specialist"
                    v-model="specialistId"
                    required
                    :disabled="specialistsLoading || Boolean(specialistsError) || specialists.length === 0"
                    :aria-invalid="Boolean(errors.specialist)"
                    :aria-describedby="errors.specialist ? 'specialist-error' : undefined"
                    @change="handleSpecialistChange"
                  >
                    <option value="">
                      {{ specialistsLoading ? 'Загружаем специалистов…' : 'Выберите специалиста' }}
                    </option>
                    <option v-for="item in specialists" :key="item.id" :value="String(item.id)">
                      {{ item.display_name }}
                    </option>
                  </select>
                  <p v-if="errors.specialist" id="specialist-error" class="field-error">
                    {{ errors.specialist }}
                  </p>
                </div>

                <div class="field">
                  <label for="service">
                    Услуга <span class="required-mark">*</span>
                  </label>
                  <select
                    id="service"
                    v-model="serviceId"
                    required
                    :disabled="!specialistId || servicesLoading || Boolean(servicesError) || services.length === 0"
                    :aria-invalid="Boolean(errors.service)"
                    :aria-describedby="errors.service ? 'service-error' : undefined"
                    @change="handleServiceChange"
                  >
                    <option value="">
                      {{ servicesLoading
                        ? 'Загружаем услуги…'
                        : !specialistId
                          ? 'Сначала выберите специалиста'
                          : 'Выберите услугу' }}
                    </option>
                    <option v-for="item in services" :key="item.id" :value="String(item.id)">
                      {{ item.name }}
                    </option>
                  </select>
                  <p v-if="errors.service" id="service-error" class="field-error">
                    {{ errors.service }}
                  </p>
                </div>
              </div>

              <div v-if="specialistsError" class="load-error" role="alert">
                <p>{{ specialistsError }}</p>
                <button type="button" class="text-button" @click="retrySpecialists">
                  Повторить загрузку <span aria-hidden="true">↻</span>
                </button>
              </div>
              <div v-if="servicesError" class="load-error" role="alert">
                <p>{{ servicesError }}</p>
                <button type="button" class="text-button" @click="retryServices">
                  Повторить загрузку <span aria-hidden="true">↻</span>
                </button>
              </div>
              <p
                v-if="!specialistsLoading && !specialistsError && specialists.length === 0"
                class="empty-note"
                role="status"
              >
                Пока нет доступных специалистов. Загляните позже.
              </p>
              <p
                v-if="specialistId && !servicesLoading && !servicesError && services.length === 0"
                class="empty-note"
                role="status"
              >
                У этого специалиста пока нет доступных услуг. Выберите другого.
              </p>
              <p v-if="specialist?.description" class="specialist-description">
                {{ specialist.description }}
              </p>
              <div v-if="service" class="service-details">
                <div>
                  <span class="small-label">ВЫБРАННАЯ УСЛУГА</span>
                  <p>{{ service.description || service.name }}</p>
                </div>
                <div class="service-meta">
                  <span>{{ service.duration_minutes }} мин.</span>
                  <strong>{{ formatPrice(service) }}</strong>
                </div>
              </div>
            </section>

            <section class="form-section">
              <div class="section-heading">
                <span class="section-number">02</span>
                <div>
                  <h2>Дата и время</h2>
                  <p>Найдите подходящее окно в своём дне</p>
                </div>
              </div>
              <div class="field date-field">
                <label for="date">
                  Дата консультации <span class="required-mark">*</span>
                </label>
                <input
                  id="date"
                  v-model="date"
                  type="date"
                  required
                  :min="today"
                  :disabled="!serviceId"
                  :aria-invalid="Boolean(errors.date)"
                  :aria-describedby="`date-hint${errors.date ? ' date-error' : ''}`"
                  @change="handleDateChange"
                >
                <p id="date-hint" class="field-hint">
                  {{ !serviceId
                    ? 'Сначала выберите специалиста и услугу.'
                    : 'Дата и время по UTC. В Москве — на 3 часа позже.' }}
                </p>
                <p v-if="errors.date" id="date-error" class="field-error">
                  {{ errors.date }}
                </p>
              </div>

              <fieldset class="time-fieldset">
                <legend>Доступное время <span class="required-mark">*</span></legend>
                <div v-if="!readyForSlots" class="slots-placeholder">
                  <span class="clock-icon" aria-hidden="true">◷</span>
                  <p>
                    Здесь появится свободное время
                    <span>Выберите услугу и дату консультации</span>
                  </p>
                </div>
                <div v-if="slotsLoading" class="slots-placeholder" role="status">
                  <span class="spinner" />
                  <p>Ищем свободное время…</p>
                </div>
                <div v-if="slotsError" class="load-error" role="alert">
                  <p>{{ slotsError }}</p>
                  <button type="button" class="text-button" @click="retrySlotLoading">
                    Повторить загрузку <span aria-hidden="true">↻</span>
                  </button>
                </div>
                <div
                  v-if="readyForSlots && !slotsLoading && !slotsError && availableSlots.length === 0"
                  class="slots-placeholder"
                  role="status"
                >
                  <span class="clock-icon" aria-hidden="true">◷</span>
                  <p>
                    На эту дату свободного времени нет
                    <span>Попробуйте выбрать другой день</span>
                  </p>
                </div>
                <div
                  v-if="!slotsLoading && !slotsError && availableSlots.length > 0"
                  class="slot-grid"
                >
                  <label
                    v-for="slot in availableSlots"
                    :key="slot.start_datetime"
                    class="time-slot"
                    :class="{ selected: time === slot.start_datetime }"
                  >
                    <input
                      type="radio"
                      name="time"
                      :value="slot.start_datetime"
                      :checked="time === slot.start_datetime"
                      required
                      :aria-invalid="Boolean(errors.time)"
                      :aria-describedby="errors.time ? 'time-error' : undefined"
                      @change="selectTime(slot.start_datetime)"
                    >
                    <span>{{ formatTime(slot.start_datetime) }}</span>
                  </label>
                </div>
                <p v-if="errors.time" id="time-error" class="field-error">
                  {{ errors.time }}
                </p>
              </fieldset>
            </section>

            <section class="form-section">
              <div class="section-heading">
                <span class="section-number">03</span>
                <div>
                  <h2>Контактные данные</h2>
                  <p>Последний шаг перед созданием демозаписи</p>
                </div>
              </div>
              <div class="field-grid contact-grid">
                <div class="field">
                  <label for="contact-type">Способ связи</label>
                  <select
                    id="contact-type"
                    v-model="contactType"
                    @change="handleContactTypeChange"
                  >
                    <option value="telegram">Telegram</option>
                    <option value="phone">Телефон</option>
                  </select>
                </div>
                <div class="field">
                  <label for="contact">
                    {{ contactType === 'telegram' ? 'Имя пользователя Telegram' : 'Номер телефона' }}
                    <span class="required-mark">*</span>
                  </label>
                  <input
                    id="contact"
                    v-model="contact"
                    :type="contactType === 'phone' ? 'tel' : 'text'"
                    autocomplete="off"
                    autocapitalize="none"
                    :spellcheck="false"
                    :maxlength="contactType === 'telegram' ? 33 : 30"
                    required
                    :placeholder="contactType === 'telegram' ? '@demo_user' : '+7 (999) 000-00-00'"
                    :aria-invalid="Boolean(errors.contact)"
                    :aria-describedby="`contact-hint${errors.contact ? ' contact-error' : ''}`"
                    @input="clearErrors('contact')"
                  >
                  <p v-if="errors.contact" id="contact-error" class="field-error">
                    {{ errors.contact }}
                  </p>
                </div>
              </div>
              <p id="contact-hint" class="field-hint demo-contact-hint">
                Используйте вымышленные данные — это демо.
                <button type="button" class="text-button" @click="fillExampleContact">
                  Заполнить примером
                </button>
              </p>
              <div class="field description-field">
                <label for="description">
                  Что хотели бы обсудить?
                  <span class="optional-label">Необязательно</span>
                </label>
                <textarea
                  id="description"
                  v-model="description"
                  rows="3"
                  maxlength="1000"
                  placeholder="Например: хочу научиться лучше планировать время для отдыха"
                  aria-describedby="description-hint"
                />
                <div class="textarea-footer">
                  <span id="description-hint">Не указывайте личные и чувствительные сведения.</span>
                  <span>{{ description.length }}/1000</span>
                </div>
              </div>
              <p class="required-hint">* Обязательные поля</p>
            </section>
          </fieldset>
        </form>
      </div>

      <aside class="booking-sidebar" aria-label="Сводка записи">
        <section v-if="appointment" class="summary-card">
          <div class="summary-heading">
            <span class="eyebrow">ВАША КОНСУЛЬТАЦИЯ</span>
            <span class="summary-flower" aria-hidden="true">✳</span>
          </div>
          <h2>Всё на своих местах</h2>
          <p class="summary-intro">
            Сохраните детали вашей демозаписи.
          </p>
          <dl class="summary-list">
            <div>
              <dt>Специалист</dt>
              <dd>
                {{ specialist?.display_name }}
              </dd>
            </div>
            <div>
              <dt>Услуга</dt>
              <dd>
                {{ service?.name }}
              </dd>
            </div>
            <div>
              <dt>Дата и время</dt>
              <dd>
                {{ formatDay(date) }}
                <span class="summary-time">{{ formatTime(time) }} · UTC</span>
              </dd>
            </div>
            <div>
              <dt>Длительность</dt>
              <dd>{{ service?.duration_minutes }} мин.</dd>
            </div>
          </dl>
          <div class="summary-total">
            <span>Стоимость</span>
            <strong>{{ formatPrice(service) }}</strong>
          </div>
        </section>

        <section v-else class="booking-action" aria-label="Создание записи">
          <button
            class="primary-button"
            type="submit"
            form="booking-form"
            :disabled="isSubmitting || specialistsLoading || servicesLoading || slotsLoading"
          >
            <template v-if="isSubmitting">
              <span class="spinner" /> Создаём запись…
            </template>
            <template v-else>
              Создать демозапись <span aria-hidden="true">↗</span>
            </template>
          </button>
          <p class="submit-caption">
            Учебная запись. Без оплаты<br>и реальной консультации.
          </p>
          <div v-if="submitError" class="submit-error" role="alert">
            {{ submitError }}
          </div>
          <p v-if="Object.keys(errors).length > 0" class="field-error" role="alert">
            Проверьте отмеченные поля формы.
          </p>
        </section>

        <section id="how-it-works" class="how-card">
          <h3>Всё начинается с одного шага</h3>
          <ol>
            <li :class="{ active: progress >= 1 }"><span>1</span>Выберите специалиста</li>
            <li :class="{ active: progress >= 2 }"><span>2</span>Найдите удобное время</li>
            <li :class="{ active: progress >= 3 }"><span>3</span>Создайте демозапись</li>
          </ol>
          <p>Можно менять свой выбор<br>до отправки формы.</p>
        </section>
      </aside>
    </div>
  </main>

  <footer class="site-footer page-width">
    <span class="footer-brand">тише.</span>
    <p>Учебный проект сервиса записи на консультации</p>
    <span>С заботой о деталях <span aria-hidden="true">✳</span></span>
  </footer>
</template>
