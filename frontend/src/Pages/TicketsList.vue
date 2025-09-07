<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const tickets = ref([])

const estado = ref('')
const tecnicoId = ref('')
const page = ref(1)
const size = ref(10)
const total = ref(0)

const tecnicos = ref([])
const ESTADOS = ['Nuevo', 'Abierto', 'En Progreso', 'Cerrado']

async function loadTecnicos() {
  try {
    const { data } = await api.get('/tecnicos')
    tecnicos.value = data
  } catch {}
}

function hydrate(list) {
  return list.map(t => ({
    ...t,
    Titulo: t.Titulo?.replace(/\n/g, ' ').replace(/,/g, ';') ?? '',
    Descripcion: t.Descripcion?.replace(/\n/g, ' ').replace(/,/g, ';') ?? '',
    _estadoNuevo: t.Estado,
    _tecnicoNuevo: t.TecnicoID ?? null,
  }))
}

async function loadTickets() {
  try {
    loading.value = true
    error.value = ''
    const params = {}
    if (estado.value) params.estado = estado.value
    if (tecnicoId.value) params.tecnico_id = tecnicoId.value
    params.page = page.value
    params.size = size.value
    const { data, headers } = await api.get('/tickets', { params })
    tickets.value = hydrate(data)
    total.value = Number(headers['x-total-count'] || 0)
  } catch {
    error.value = 'No se pudo cargar la lista de tickets'
  } finally {
    loading.value = false
  }
}

function goNew() { router.push({ name: 'ticket-new' }) }
function goDetail(id) { router.push({ name: 'ticket-detail', params: { id } }) }

async function changeEstado(t) {
  try {
    if (t._estadoNuevo === 'Cerrado' && !t.TecnicoID) {
      alert('No puedes cerrar un ticket sin técnico asignado.')
      t._estadoNuevo = t.Estado
      return
    }
    await api.put('/tickets/', { TicketID: t.TicketID, Estado: t._estadoNuevo })
    t.Estado = t._estadoNuevo
  } catch (e) {
    alert(e?.response?.data?.detail || 'Error al cambiar estado')
    t._estadoNuevo = t.Estado
  }
}

async function assignTecnico(t) {
  try {
    const body = { TicketID: t.TicketID, TecnicoID: t._tecnicoNuevo ?? null }
    await api.put('/tickets/', body)
    t.TecnicoID = t._tecnicoNuevo ?? null
  } catch (e) {
    alert(e?.response?.data?.detail || 'Error al asignar técnico')
    t._tecnicoNuevo = t.TecnicoID ?? null
  }
}

async function borrarTicket(t) {
  const ok = confirm(`¿Eliminar el ticket #${t.TicketID}?`)
  if (!ok) return
  try {
    await api.delete(`/tickets/${t.TicketID}`)
    await loadTickets()
  } catch (e) {
    alert(e?.response?.data?.detail || 'Error al eliminar')
  }
}

function exportCSV() {
  const rows = [
    ['TicketID','Titulo','Descripcion','Estado','UsuarioID','TecnicoID','FechaCreacion'],
    ...tickets.value.map(t => [
      t.TicketID,
      t.Titulo ?? '',
      t.Descripcion ?? '',
      t.Estado ?? '',
      t.UsuarioID ?? '',
      t.TecnicoID ?? '',
      t.FechaCreacion ? new Date(t.FechaCreacion).toISOString() : ''
    ])
  ]
  const csv = rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type:'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'tickets.csv'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => { await Promise.all([loadTecnicos(), loadTickets()]) })
</script>

<template>
  <section class="container wide">
    <h2 class="ttl">Mesa de Ayuda — Tickets</h2>

    <div class="filters">
      <label>Estado:
        <select v-model="estado" @change="loadTickets">
          <option value="">(Todos)</option>
          <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
        </select>
      </label>

      <label>TécnicoID:
        <input v-model="tecnicoId" type="number" min="1" placeholder="Ej. 2" @keyup.enter="loadTickets" />
      </label>

      <label>Página:
        <input v-model.number="page" type="number" min="1" @change="loadTickets" />
      </label>

      <label>Tamaño:
        <input v-model.number="size" type="number" min="1" max="100" @change="loadTickets" />
      </label>

      <span class="muted">Total: {{ total }}</span>

      <div class="filters-actions">
        <button class="btn ghost" @click="loadTickets">Actualizar</button>
        <button class="btn ghost" @click="exportCSV">Exportar CSV</button>
        <button class="btn primary" @click="goNew">+ Nuevo ticket</button>
      </div>
    </div>

    <p v-if="loading">Cargando...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="tickets.length" class="table-wrap">
      <table class="tickets">
        <colgroup>
          <col style="width:64px" />
          <col style="width:380px" />
          <col style="width:520px" />
          <col style="width:140px" />
          <col style="width:170px" />
          <col style="width:110px" />
          <col style="width:120px" />
          <col style="width:170px" />
          <col style="width:180px" />
          <col style="width:160px" />
        </colgroup>

        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Descripción</th>
            <th>Estado</th>
            <th>Cambiar<br>estado</th>
            <th>UsuarioID</th>
            <th>Técnico</th>
            <th>Asignar<br>técnico</th>
            <th>Creado</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="t in tickets" :key="t.TicketID">
            <td class="td-id">{{ t.TicketID }}</td>

            <td class="td-title">
              <div class="cell clamp" :title="t.Titulo">{{ t.Titulo }}</div>
            </td>

            <td class="td-desc">
              <div class="cell clamp" :title="t.Descripcion">{{ t.Descripcion }}</div>
            </td>

            <td class="td-state">
              <span class="badge" :data-estado="t.Estado">{{ t.Estado }}</span>
            </td>

            <td class="td-change">
              <select v-model="t._estadoNuevo" @change="changeEstado(t)" class="sel-sm">
                <option value="Nuevo">Nuevo</option>
                <option value="Abierto">Abierto</option>
                <option value="En Progreso">En Progreso</option>
                <option value="Cerrado">Cerrado</option>
              </select>
            </td>

            <td class="td-num">{{ t.UsuarioID }}</td>
            <td class="td-num">{{ t.TecnicoID ?? '—' }}</td>

            <td class="td-assign">
              <select v-model="t._tecnicoNuevo" @change="assignTecnico(t)" class="sel-sm">
                <option :value="null">(Sin técnico)</option>
                <template v-if="tecnicos.length">
                  <option v-for="tec in tecnicos" :key="tec.TecnicoID" :value="tec.TecnicoID">
                    {{ tec.TecnicoID }} — {{ tec.Apenom }}
                  </option>
                </template>
                <template v-else>
                  <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                </template>
              </select>
            </td>

            <td class="td-created">{{ new Date(t.FechaCreacion).toLocaleString() }}</td>

            <td class="td-actions">
              <button @click="goDetail(t.TicketID)" class="btn btn-light">Ver</button>
              <button @click="borrarTicket(t)" class="btn btn-danger">Borrar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else-if="!loading">No hay tickets</p>
  </section>
</template>

<style scoped>
.container{ max-width:1280px; margin:0 auto; padding:12px 16px; }
.container.wide{ max-width:min(1800px, calc(100vw - 48px)); }
.ttl{ margin:8px 0 14px; }

.table-wrap{ overflow-x:auto; }
.tickets{ width:100%; border-collapse:collapse; table-layout:fixed; }

.tickets th,.tickets td{
  box-sizing:border-box;
  border-bottom:1px solid rgba(255,255,255,.08);
  padding:.65rem 1rem;
  vertical-align:top;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:normal;
}
.tickets thead th{
  position:sticky; top:0; z-index:2;
  background:rgba(17,24,39,.92);
  white-space:nowrap;
}


.td-title .cell,
.td-desc  .cell{
  display:-webkit-box;
  -webkit-box-orient:vertical;
  -webkit-line-clamp:2;
  overflow:hidden;
  word-break:break-word;
}

/* separateeeeeeeeeee */
.td-title { min-width:300px; }
.td-desc  { min-width:520px; }

.td-id,.td-num{ white-space:nowrap; }
.td-actions{ display:flex; gap:.5rem; }

.filters{ display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-bottom:12px; }
.filters-actions{ margin-left:auto; display:flex; gap:8px; }
.muted{ opacity:.8; }

.sel-sm{ padding:6px 8px; border-radius:8px; background:rgba(17,24,39,.6); border:1px solid rgba(148,163,184,.25); color:#e5e7eb; }

.btn{ padding:6px 10px; border-radius:8px; border:1px solid transparent; }
.btn.primary{ background:rgba(99,102,241,.18); border-color:rgba(99,102,241,.45); }
.btn.ghost{ background:rgba(148,163,184,.12); border-color:rgba(148,163,184,.35); }
.btn-light{ background:rgba(99,102,241,.12); border:1px solid rgba(99,102,241,.35); }
.btn-danger{ background:rgba(239,68,68,.12); border:1px solid rgba(239,68,68,.35); }

.badge{ display:inline-block; padding:4px 8px; border-radius:999px; font-size:.82rem; border:1px solid rgba(255,255,255,.1); background:rgba(255,255,255,.05); }
.badge[data-estado="Nuevo"]{ background:rgba(99,102,241,.14); border-color:rgba(99,102,241,.35); }
.badge[data-estado="Abierto"]{ background:rgba(34,197,94,.14); border-color:rgba(34,197,94,.35); }
.badge[data-estado="En Progreso"]{ background:rgba(234,179,8,.18); border-color:rgba(234,179,8,.4); }
.badge[data-estado="Cerrado"]{ background:rgba(148,163,184,.14); border-color:rgba(148,163,184,.35); }

.error{ color:#ffb4b4; }
</style>
