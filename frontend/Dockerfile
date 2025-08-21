# --- Estágio 1: Instalar dependências ---
FROM node:18-alpine AS deps
WORKDIR /app

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Copiar APENAS os arquivos de dependência primeiro (para cache)
COPY package.json pnpm-lock.yaml* ./

# Instalar dependências de produção
RUN pnpm install --prod --frozen-lockfile || pnpm install --prod

# --- Estágio 2: Construir a aplicação ---
FROM node:18-alpine AS builder
WORKDIR /app

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Copiar APENAS os arquivos de dependência primeiro
COPY package.json pnpm-lock.yaml* ./

# Instalar TODAS as dependências
RUN pnpm install --frozen-lockfile || pnpm install

# Agora copiar o código fonte (que muda com mais frequência)
COPY . .

# Construir a aplicação
RUN pnpm build

# --- Estágio 3: Imagem final ---
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copiar apenas o necessário para produção
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.js ./next.config.js
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json

EXPOSE 3000

CMD ["node_modules/.bin/next", "start"]