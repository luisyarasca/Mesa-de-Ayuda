<template>
  <div class="card" style="padding:1rem">
    <div class="header" style="margin-bottom:.5rem">
      <div style="display:flex; align-items:center; gap:.75rem;">
        <RouterLink class="link" to="/tickets">← Volver</RouterLink>
        <h1 style="margin:0">Ticket #{{ ticket?.TicketID }}</h1>
      </div>
      <span v-if="ticket" :class="statusClass(ticket.Estado)">{{ ticket.Estado }}</span>
    </div>

    <p v-if="loading">Cargando…</p>
    <p v-else-if="error" style="color:#ffb4b4">{{ error }}</p>

    <section v-else class="container" style="grid-template-columns: 1fr 320px;">
      <div class="card">
        <h2 style="margin-top:0">{{ ticket.Titulo }}</h2>
        <p style="color:var(--muted); white-space:pre-wrap">{{ ticket.Descripcion }}</p>

        <h3>Comentarios</h3>
        <ul style="display:grid; gap:.6rem; list-style:none; padding:0; margin:0 0 1rem 0;">
          <li v-for="c in comments" :key="c.ComentarioID" class="card" style="padding:.7rem">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b>{{ c.Autor }}</b>
              <small style="color:var(--muted)">{{ new Date(c.Fecha).toLocaleString() }}</small>
            </div>
            <div style="margin-top:.35rem; white-space:pre-wrap">{{ c.Contenido }}</div>
          </li>
          <li v-if="!comments.length" class="empty">Aún no hay comentarios</li>
        </ul>

        <form class="card" @submit.prevent="addComment">
          <h3 style="margin-top:0">Agregar comentario</h3>
          <div style="display:grid; gap:.6rem;">
            <input v-model="comment.Autor" placeholder="Autor" required />
            <textarea v-model="comment.Contenido" placeholder="Comentario" required minlength="2"></textarea>
          </div>
          <div style="margin-top:.6rem; display:flex; gap:.5rem; justify-content:flex-end;">
            <button type="submit" class="btn btn-primary" :disabled="saving">Enviar</button>
          </div>
        </form>
      </div>

      <aside class="card">
        <div class="meta">
          <div class="meta__row"><div class="meta__key">UsuarioID</div><div>{{ ticket.UsuarioID }}</div></div>
          <div class="meta__row"><div class="meta__key">TécnicoID</div><div>{{ ticket.TecnicoID ?? '—' }}</div></div>
          <div class="meta__row"><div class="meta__key">Creado</div><div>{{ new Date(ticket.FechaCreacion).toLocaleString() }}</div></div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRoute, RouterLink } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const id = route.params.id;

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const ticket = ref(null);
const comments = ref([]);
const comment = reactive({ Autor: "", Contenido: "" });

function statusClass(s) {
  switch (s) {
    case 'Nuevo': return 'badge badge--new'
    case 'Abierto': return 'badge badge--open'
    case 'En Progreso': return 'badge badge--progress'
    case 'Cerrado': return 'badge badge--closed'
    default: return 'badge'
  }
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [t, cs] = await Promise.all([
      api.get(`/tickets/id/${id}`),
      api.get(`/tickets/${id}/comentarios`),
    ]);
    ticket.value = t.data;
    comments.value = cs.data;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Error al cargar";
  } finally {
    loading.value = false;
  }
}

async function addComment() {
  saving.value = true;
  try {
    const { data } = await api.post(`/tickets/${id}/comentarios`, comment);
    comments.value.unshift(data);
    comment.Autor = "";
    comment.Contenido = "";
  } catch (e) {
    alert(e?.response?.data?.detail || "Error al comentar");
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>
