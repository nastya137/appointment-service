function App() {
  return (
    <main>
      <h1>Запись на консультацию</h1>

      <form>
        <section>
          <h2>Услуга</h2>
          <button type="button">Индивидуальная консультация</button>
          <button type="button">Консультация для пары</button>
        </section>

        <section>
          <h2>Специалист</h2>
          <button type="button">Анна Иванова</button>
        </section>

        <section>
          <h2>Дата</h2>
          <button type="button">10 августа</button>
          <button type="button">11 августа</button>
          <button type="button">12 августа</button>
        </section>

        <section>
          <h2>Время</h2>
          <button type="button">09:00</button>
          <button type="button">10:00</button>
          <button type="button">11:00</button>
          <button type="button">14:00</button>
        </section>

        <section>
          <h2>Контакт</h2>

          <label>
            Telegram
            <input type="text" placeholder="@username" />
          </label>
        </section>

        <section>
          <h2>Описание проблемы</h2>

          <textarea
            placeholder="Расскажите, с чем хотели бы обратиться"
            rows={5}
          />
        </section>

        <button type="submit">
          Записаться
        </button>
      </form>
    </main>
  )
}

export default App