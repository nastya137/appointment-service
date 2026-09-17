import { ref, toValue, watch } from 'vue'
import type { MaybeRefOrGetter } from 'vue'
import { requestJson } from './api'

export function useResource<T>(path: MaybeRefOrGetter<string | null>) {
  const data = ref<T[]>([])
  const error = ref<string>()
  const loading = ref(false)
  const attempt = ref(0)

  watch([() => toValue(path), attempt], ([currentPath], _, onCleanup) => {
    data.value = []
    error.value = undefined
    loading.value = Boolean(currentPath)
    if (!currentPath) return

    const controller = new AbortController()
    let active = true
    const timeout = window.setTimeout(() => controller.abort(), 15000)

    requestJson<T[]>(currentPath, { signal: controller.signal })
      .then((responseData) => {
        if (!Array.isArray(responseData)) throw new Error('Expected a list')
        if (active) {
          data.value = responseData
          error.value = undefined
        }
      })
      .catch(() => {
        if (active) {
          error.value =
            'Не удалось загрузить данные. Проверьте соединение и попробуйте ещё раз.'
        }
      })
      .finally(() => {
        window.clearTimeout(timeout)
        if (active) loading.value = false
      })

    onCleanup(() => {
      active = false
      controller.abort()
      window.clearTimeout(timeout)
    })
  }, { immediate: true })

  return {
    data,
    error,
    loading,
    retry: () => { attempt.value += 1 },
  }
}
