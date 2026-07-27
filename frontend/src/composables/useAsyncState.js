import { onBeforeUnmount, reactive } from 'vue'
import { readableError } from '@/api/client'

export function useAsyncState(loader, fallbackMessage) {
  const state = reactive({
    loading: false,
    error: '',
    status: null,
    data: null,
  })
  let controller = null

  async function run(...args) {
    if (controller) controller.abort()
    controller = new AbortController()
    state.loading = true
    state.error = ''
    state.status = null
    try {
      state.data = await loader(...args, controller.signal)
      state.status = 200
      return state.data
    } catch (error) {
      if (error.name !== 'CanceledError' && error.code !== 'ERR_CANCELED') {
        state.status = error.response?.status || null
        state.error = readableError(error, fallbackMessage)
      }
      return null
    } finally {
      state.loading = false
    }
  }

  onBeforeUnmount(() => {
    if (controller) controller.abort()
  })

  return { state, run }
}
