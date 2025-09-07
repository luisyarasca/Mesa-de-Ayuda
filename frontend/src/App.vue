<template>
  <div class="layout">
    <header class="topbar">
      <div class="brand">Mesa de Ayuda</div>
      <nav class="nav">
        <RouterLink to="/tickets" class="link" active-class="active">Tickets</RouterLink>
        <RouterLink to="/dashboard" class="link" active-class="active">Dashboard</RouterLink>
      </nav>
      <RouterLink to="/tickets/new" class="btn-primary">Nuevo</RouterLink>
    </header>

    <main class="page">
      <RouterView />
    </main>

    <footer class="footer">Hecho con FastAPI + Vue · 2025</footer>
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; display: grid; grid-template-rows: auto 1fr auto; }
.topbar {
  position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px; backdrop-filter: blur(6px);
  background: linear-gradient(90deg, rgba(15,20,35,0.85), rgba(15,20,35,0.4));
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.brand { font-weight: 700; letter-spacing: .3px; }
.nav { display: flex; gap: 12px; }
.link { padding: 6px 10px; border-radius: 8px; opacity: .8; }
.link:hover { background: rgba(255,255,255,.06); opacity: 1; }
.link.active { background: rgba(99,102,241,.18); border: 1px solid rgba(99,102,241,.35); }
.btn-primary {
  padding: 8px 12px; border-radius: 10px;
  background: linear-gradient(90deg, #6366f1, #22d3ee);
  color: #0b1020; font-weight: 700;
}
.page { padding: 16px 22px; }
.footer { text-align: center; padding: 14px; opacity: .7; }
</style>

