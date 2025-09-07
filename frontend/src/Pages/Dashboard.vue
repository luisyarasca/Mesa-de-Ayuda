<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const loading = ref(false)
const err = ref('')
const stats = ref({ Total: 0, Nuevos: 0, Abiertos: 0, 'En Progreso': 0, Cerrados: 0 })

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get('/tickets/estadisticas')
    stats.value = data
  } catch (e) {
    err.value = 'No se pudo cargar estadísticas'
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <main class="wrap">
    <h1>Dashboard</h1>
    <p v-if="loading">Cargando…</p>
    <p v-else-if="err" class="err">{{ err }}</p>
    <section v-else class="grid">
      <article class="card">
        <h3>Total</h3>
        <div class="num">{{ stats.Total }}</div>
      </article>
      <article class="card">
        <h3>Nuevo</h3>
        <div class="num">{{ stats.Nuevos }}</div>
      </article>
      <article class="card">
        <h3>Abierto</h3>
        <div class="num">{{ stats.Abiertos }}</div>
      </article>
      <article class="card">
        <h3>En Progreso</h3>
        <div class="num">{{ stats['En Progreso'] }}</div>
      </article>
      <article class="card">
        <h3>Cerrado</h3>
        <div class="num">{{ stats.Cerrados }}</div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.wrap { max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
.card { border: 1px solid #eee; border-radius: .75rem; padding: 1rem; background: #fff; }
.num { font-size: 2rem; font-weight: 700; }
.err { color: #c00; }
</style>
