import type { Service } from '../entities/service/model/types'

export type ContactType = 'telegram' | 'phone'

// The current API builds its working schedule in UTC. Keep the selected day
// and displayed slots in that same zone; SQLite may return naive timestamps.
export function parseApiDate(value: string) {
  return new Date(/(?:Z|[+-]\d{2}:?\d{2})$/i.test(value) ? value : `${value}Z`)
}

export function formatTime(value: string) {
  return parseApiDate(value).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
  })
}

export function formatDay(value: string) {
  return new Date(`${value}T12:00:00Z`).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

export function formatPrice(service?: Service) {
  if (!service || service.price === null) return 'Стоимость не указана'
  if (!service.currency)
    return `${service.price.toLocaleString('ru-RU')} · валюта не указана`
  try {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: service.currency,
      maximumFractionDigits: 2,
    }).format(service.price)
  } catch {
    return `${service.price.toLocaleString('ru-RU')} ${service.currency}`
  }
}

export function validateContact(
  value: string,
  type: ContactType,
): string | undefined {
  if (!value.trim())
    return type === 'telegram'
      ? 'Укажите имя пользователя Telegram.'
      : 'Укажите номер телефона.'
  if (
    type === 'telegram' &&
    !/^@?[a-zA-Z][a-zA-Z0-9_]{4,31}$/.test(value.trim())
  ) {
    return 'Введите username: 5–32 латинских символа, цифры или _. Первый символ — буква.'
  }
  if (
    type === 'phone' &&
    (!/^\+?[\d\s()-]+$/.test(value.trim()) ||
      !/^\d{10,15}$/.test(value.replace(/\D/g, '')))
  ) {
    return 'Введите телефон с кодом страны: от 10 до 15 цифр.'
  }
}

export function normalizeContact(value: string, type: ContactType) {
  return type === 'telegram'
    ? `@${value.trim().replace(/^@/, '')}`
    : value.trim().replace(/[\s()-]/g, '')
}
