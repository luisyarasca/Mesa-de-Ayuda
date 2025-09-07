<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const stats = ref({ Total: 0, Nuevos: 0, Abiertos: 0, 'En Progreso': 0, Cerrados: 0 })
const loading = ref(true)
const error = ref('')

async function load() {
  try {
    const { data } = await api.get('/tickets/estadisticas')
    stats.value = data
  } catch {
    error.value = 'No se pudo cargar las estadísticas'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="container wide">
    <h2 class="ttl">Dashboard</h2>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="kpis" v-if="!loading">
      <div class="card total">
        <span class="label">Total</span>
        <span class="value">{{ stats.Total }}</span>
      </div>

      <div class="card nuevo">
        <span class="label">Nuevo</span>
        <span class="value">{{ stats.Nuevos }}</span>
      </div>

      <div class="card abierto">
        <span class="label">Abierto</span>
        <span class="value">{{ stats.Abiertos }}</span>
      </div>

      <div class="card progreso">
        <span class="label">En Progreso</span>
        <span class="value">{{ stats['En Progreso'] }}</span>
      </div>

      <div class="card cerrado">
        <span class="label">Cerrado</span>
        <span class="value">{{ stats.Cerrados }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ancho cómodo como en Tickets */
.container { max-width: min(1400px, calc(100vw - 48px)); margin: 0 auto; padding: 18px 16px; }
.container.wide { max-width: min(1800px, calc(100vw - 48px)); }
@media (min-width: 1920px) {
  .container.wide { max-width: min(2000px, calc(100vw - 64px)); }
}

.ttl { margin: 8px 0 18px; font-weight: 800; font-size: 2rem; letter-spacing: .2px; }

.kpis {
  display: grid;
  grid-template-columns: repeat(5, minmax(180px, 1fr));
  gap: 16px;
}

/* tarjeta base */
.card {
  position: relative;
  border-radius: 16px;
  padding: 18px 20px;
  border: 1px solid rgba(255,255,255,.08);
  background: rgba(255,255,255,.04);
  box-shadow:
    0 6px 18px rgba(0,0,0,.25),
    inset 0 1px 0 rgba(255,255,255,.06);
  backdrop-filter: blur(4px);
}

.card .label { font-weight: 600; opacity: .9; }
.card .value { display: block; margin-top: 6px; font-size: 2.35rem; font-weight: 800; line-height: 1.15; }

/* Colores (mismos tonos que tus badges) */
.total {
  background: linear-gradient(180deg, rgba(99,102,241,.22), rgba(99,102,241,.08));
  border-color: rgba(99,102,241,.35);
}

.nuevo {
  background: linear-gradient(180deg, rgba(99,102,241,.22), rgba(99,102,241,.08));
  border-color: rgba(99,102,241,.45);
}

.abierto {
  background: linear-gradient(180deg, rgba(34,197,94,.22), rgba(34,197,94,.08));
  border-color: rgba(34,197,94,.45);
}

.progreso {
  background: linear-gradient(180deg, rgba(234,179,8,.25), rgba(234,179,8,.08));
  border-color: rgba(234,179,8,.45);
}

.cerrado {
  background: linear-gradient(180deg, rgba(148,163,184,.20), rgba(148,163,184,.08));
  border-color: rgba(148,163,184,.35);
}

/* responsive */
@media (max-width:1200px) {
  .kpis { grid-template-columns: repeat(3, minmax(180px, 1fr)); }
}
@media (max-width:780px) {
  .kpis { grid-template-columns: repeat(2, minmax(160px, 1fr)); }
}
@media (max-width:520px) {
  .kpis { grid-template-columns: 1fr; }
}

.error { color:#ffb4b4; }
</style>
