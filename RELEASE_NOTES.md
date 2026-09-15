# 🚀 Release Notes — KDE Webapp Manager v1.2.0

> **Redesenho Brutalista Oriental Minimalista & Sistema de Decorações de Vanguarda**

---

## 🎨 Nova Identidade Visual & UI Design System

### 1. Paleta de Cores e Tokens Foscos (Strict Palette)
- **Canvas / Fundo Geral (`surface-0`):** `#090a0f` (Carvão/Obsidiana mineral fosco profundo).
- **Painéis / Cards (`surface-1`):** `#14171f` (Grafite industrial fosco com bordas translúcidas).
- **Superfícies Interativas (`surface-2`):** `#1c242c` (Hover tátil e elevação suave).
- **Tipografia & Linhas (`text-primary` / `text-muted`):** Off-white nítido (`#dedfd7`) e cinza industrial suave (`#7e8790`).
- **Cor de Assinatura (Accent Color):** **Azul Cobalto Elétrico (`#2563eb` / `#3b82f6`)** com grifos cirúrgicos e selos em **Vermelho Hanko Vermilion (`#E63946`)**.

---

## ⛩️ Novo Sistema de Micro-Decorações

- 🏁 **`DotMatrixCanvas` (Malha de Micro-Pontos):** Textura de *Dot Matrix* sutil integrada no fundo dos cards Bento Grid sem ruído visual.
- 🧧 **Hanko Seal Stamp Badges (Carimbos Orientais):**
  - `[ 網 ]` — *Sys.Katalog / Webapps* (Cobalt Blue)
  - `[ 設 ]` — *Informações Básicas do App* (Cobalt Blue)
  - `[ 視 ]` — *Janela & Identidade Visual* (Cobalt Blue)
  - `[ 規 ]` — *Regras KWin & Isolamento* (Hanko Vermilion)
  - `[ 執 ]` — *Comandos de Execução Terminal* (Cobalt Blue)
- ➕ **Technical Crosshairs (`+ + + +`):** Sequências rítmicas de cruzes técnicas em monospace para alinhamento e respiro espacial.
- 💊 **Status Indicator Pills:** Cápsulas translúcidas com indicadores de status com aura radiante (`● SYS.READY`, `● ONLINE`).
- ⛩️ **Vertical Kanji/Katakana Rulers (Conceito 'Ma'):** Colunas verticais estruturais (`ウェブアプリ // 制御`, `構造`, `管理`) atuando como réguas de margem e respiro tátil no layout.

---

## 🖼️ Novo Logo Oficial da Aplicação

- **Identidade Vetorial Exclusiva:** Novo ícone oficial combinando silhueta geométrica de janela de navegador, núcleo de matriz em Azul Cobalto Elétrico, anéis wireframe técnicos, malha de pontos e selo Hanko em vermelho vermilion sobre fundo obsidiana fosco.
- **Integração Total:** Atualizado na janela do aplicativo, barra de tarefas do KDE, menu de aplicativos do sistema (K-Menu) e no `README.md`.

---

## 🛠️ Melhores de Desempenho e Estabilidade

- **Mapeamento KWin & Wayland Aprimorado:** Resolução dinâmica de `StartupWMClass` / `WM_CLASS` para navegadores nativos e Flatpak (Chrome, Brave, Edge, Vivaldi, Chromium).
- **Sincronização via DBus:** Recarregamento instantâneo de regras de janela sem necessidade de reiniciar o Plasma.
- **Bateria de Testes Unitários:** 100% de cobertura nos módulos de modelo, GUI e decorações visual (15/15 testes aprovados).

---

## 📦 Como Atualizar / Executar

```bash
git pull origin main
./install.sh
```

---

*Desenvolvido para o KDE Plasma desktop environment.*
