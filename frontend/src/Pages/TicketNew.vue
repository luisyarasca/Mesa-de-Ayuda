<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const saving = ref(false)
const error = ref('')

const form = reactive({
  Titulo: '',
  Descripcion: '',
  UsuarioID: '',
  TecnicoID: ''
})

async function submit() {
  error.value = ''
  saving.value = true
  try {
    // manda null
    const payload = {
      Titulo: form.Titulo,
      Descripcion: form.Descripcion,
      UsuarioID: Number(form.UsuarioID),
      TecnicoID: form.TecnicoID ? Number(form.TecnicoID) : null
    }
    const { data } = await api.post('/tickets/', payload)
    router.push({ name: 'ticket-detail', params: { id: data.TicketID } })
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error al crear ticket'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="card" style="padding:1rem">
    <div class="header" style="margin-bottom:.75rem">
      <h1>Nuevo Ticket</h1>
      <RouterLink class="btn" to="/tickets">Cancelar</RouterLink>
    </div>

    <form class="card" @submit.prevent="submit">
      <div style="display:grid; gap:.9rem;">
        <label class="small">
          Título
          <input v-model="form.Titulo" required minlength="3" maxlength="100" placeholder="Ej. Error SharePoint" />
        </label>

        <label class="small">
          Descripción
          <textarea v-model="form.Descripcion" required minlength="10" maxlength="500" placeholder="Describe el problema..."></textarea>
        </label>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:.9rem;">
          <label class="small">
            UsuarioID
            <input v-model="form.UsuarioID" type="number" min="1" required placeholder="Ej. 2" />
          </label>
          <label class="small">
            TécnicoID (opcional)
            <input v-model="form.TecnicoID" type="number" min="1" placeholder="Ej. 1" />
          </label>
        </div>
      </div>

      <div v-if="error" style="color:#ffb4b4; margin-top:.6rem">{{ error }}</div>

      <div style="margin-top:1rem; display:flex; gap:.5rem; justify-content:flex-end;">
        <button type="button" class="btn" @click="$router.push('/tickets')">Cancelar</button>
        <button type="submit" class="btn btn-primary" :disabled="saving">Crear</button>
      </div>
    </form>
  </div>
</template>
