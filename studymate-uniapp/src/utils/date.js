export const dateUtil = {
  format(date, format = 'YYYY-MM-DD') {
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    const seconds = String(d.getSeconds()).padStart(2, '0')

    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds)
  },

  today() {
    return this.format(new Date())
  },

  yesterday() {
    const d = new Date()
    d.setDate(d.getDate() - 1)
    return this.format(d)
  },

  tomorrow() {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    return this.format(d)
  },

  getDaysBetween(startDate, endDate) {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = Math.abs(end - start)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  },

  addDays(date, days) {
    const d = new Date(date)
    d.setDate(d.getDate() + days)
    return this.format(d)
  },

  isToday(date) {
    return this.format(date) === this.today()
  },

  isPast(date) {
    return new Date(date) < new Date(this.today())
  },

  isFuture(date) {
    return new Date(date) > new Date(this.today())
  },

  getWeekDay(date) {
    const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
    const d = new Date(date)
    return days[d.getDay()]
  },

  getMonthDays(year, month) {
    return new Date(year, month + 1, 0).getDate()
  },

  parse(dateStr) {
    return new Date(dateStr)
  }
}