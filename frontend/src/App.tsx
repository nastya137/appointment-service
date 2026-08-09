import { useState, useEffect } from 'react'
import type { Specialist } from './entities/specialist/model/types'
import type { Service } from './entities/service/model/types'
import type { AvailableSlot } from './entities/appointment/model/types'  

function App() {

  const [specialists, setSpecialists] = useState<Specialist[]>([])
  const [selectedSpecialistId, setSelectedSpecialistId] =
    useState<number | null>(null)
  const [services, setServices] = useState<Service[]>([])
  const [selectedService, setSelectedService] =
    useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState('')
  const [availableSlots, setAvailableSlots] =
  useState<AvailableSlot[]>([])
  const [selectedTime, setSelectedTime] =
    useState('')
  const [contact, setContact] = useState('')
  const [description, setDescription] = useState('')
  const [userId] = useState(1)
  const [isSuccess, setIsSuccess] = useState(false)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/specialists')
      .then((response) => response.json())
      .then((data) => setSpecialists(data))
  }, [])

  useEffect(() => {
    if (selectedSpecialistId === null) {
      setServices([])
      return
    }

    fetch(
      `http://127.0.0.1:8000/services/specialist/${selectedSpecialistId}`
    )
      .then((response) => response.json())
      .then((data) => setServices(data))
  }, [selectedSpecialistId])

  useEffect(() => {
    if (
      selectedSpecialistId === null ||
      selectedService === '' ||
      selectedDate === ''
    ) {
      setAvailableSlots([])
      return
    }

    fetch(
      `http://127.0.0.1:8000/appointments/available-slots` +
      `?specialist_id=${selectedSpecialistId}` +
      `&service_id=${selectedService}` +
      `&target_date=${selectedDate}`
    )
      .then((response) => response.json())
      .then((data) => {
        setAvailableSlots(data)
      })
  }, [selectedSpecialistId, selectedService, selectedDate])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (
      selectedSpecialistId === null ||
      selectedService === '' ||
      selectedDate === '' ||
      selectedTime === '' ||
      contact === ''
    ) {
      return
    }

    const response = await fetch(
      'http://127.0.0.1:8000/appointments',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          specialist_id: selectedSpecialistId,
          service_id: Number(selectedService),
          start_datetime: selectedTime,
          contact_type: 'telegram',
          contact_value: contact,
          problem_description: description,
        }),
      }
    )

    if (!response.ok) {
      const error = await response.json()
      console.error(error)
      return
    }

    const appointment = await response.json()

    if (!response.ok) {
      const error = await response.json()
      console.error('Ошибка создания записи:', error)
      return
    }

    setIsSuccess(true)

    console.log('Запись создана:', appointment)
  }

  return (
    <main className="min-h-screen bg-gray-100 px-4 py-10">
      <div className="mx-auto max-w-2xl rounded-2xl bg-white p-6 shadow-sm sm:p-8">
        <h1 className="mb-8 text-3xl font-bold text-gray-900">
          Запись на консультацию
        </h1>
        {isSuccess && (
          <div className="mb-6 rounded-xl bg-green-100 p-4 text-green-800">
            Запись успешно создана!
          </div>
        )}
        <form
          className="space-y-8"
          onSubmit={handleSubmit}
        >

          <section>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
              Специалист
            </h2>
            <select
              value={selectedSpecialistId ?? ''}
              onChange={(event) => {
                setSelectedSpecialistId(Number(event.target.value))
              }}
              className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none transition focus:border-black"
            >
              <option value="" disabled>
                Выберите специалиста
              </option>

              {specialists.map((specialist) => (
                <option
                  key={specialist.id}
                  value={specialist.id}
                >
                  {specialist.display_name}
                </option>
              ))}

            </select>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
              Услуга
            </h2>

            <select
              value={selectedService ?? ''}
              onChange={(event) => {
                setSelectedService(event.target.value)
              }}
              disabled={selectedSpecialistId === null}
              className="w-full rounded-xl border border-gray-300 px-4 py-3"
            >
              <option value="" disabled>
                {selectedSpecialistId === null
                  ? 'Сначала выберите специалиста'
                  : 'Выберите услугу'}
              </option>

              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name}
                </option>
              ))}
            </select>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
              Дата
            </h2>

            <input
              type="date"
              value={selectedDate}
              min={new Date().toISOString().split('T')[0]}
              onChange={(event) => setSelectedDate(event.target.value)}
              className="w-full rounded-xl border border-gray-300 px-4 py-3"
            />
          </section>

          <section>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
              Время
            </h2>

            <select
              value={selectedTime}
              onChange={(event) => setSelectedTime(event.target.value)}
              disabled={availableSlots.length === 0}
              className="w-full rounded-xl border border-gray-300 px-4 py-3"
            >
              <option value="" disabled>
                {availableSlots.length === 0
                  ? 'Нет свободного времени'
                  : 'Выберите время'}
              </option>

              {availableSlots.map((slot) => {
                const start = new Date(slot.start_datetime)

                const time = start.toLocaleTimeString('ru-RU', {
                  hour: '2-digit',
                  minute: '2-digit',
                })

                return (
                  <option
                    key={slot.start_datetime}
                    value={slot.start_datetime}
                  >
                    {time}
                  </option>
                )
              })}
            </select>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
              Контакт
            </h2>

            <input
              type="text"
              value={contact}
              onChange={(event) => setContact(event.target.value)}
              placeholder="@username или номер телефона"
              className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none transition focus:border-black"
            />
          </section>

          <section>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
              Описание проблемы
            </h2>

            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Расскажите, с чем хотели бы обратиться"
              rows={5}
              className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 outline-none transition focus:border-black"
            />
          </section>

          <button
            type="submit"
            className="w-full rounded-xl bg-black px-4 py-3 font-semibold text-white transition hover:bg-gray-800"
          >
            Записаться
          </button>
        </form>
      </div>
    </main>
  )
}

export default App