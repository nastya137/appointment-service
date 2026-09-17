export interface Service {
  id: number
  name: string
  description: string | null
  duration_minutes: number
  price: number | null
  currency: string | null
}
