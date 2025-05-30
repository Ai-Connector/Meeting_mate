# ベースイメージとしてNode.jsの公式イメージを使用 (Use official Node.js image as base)
FROM node:18-alpine

# アプリケーションの作業ディレクトリを設定 (Set working directory for the application)
WORKDIR /app

# package.json と package-lock.json (または yarn.lock) をコピー (Copy package.json and package-lock.json (or yarn.lock))
# これにより、依存関係のレイヤーキャッシュが利用可能になります (This allows Docker to leverage layer caching for dependencies)
COPY package*.json ./

# 依存関係をインストール (Install dependencies)
# npm ci を使用すると、package-lock.json に基づいてクリーンインストールが行われます (Using npm ci for a clean install based on package-lock.json)
RUN npm ci

# アプリケーションコードの残りをコピー (Copy the rest of the application code)
# これには、pages, public, generated, next.config.js, tsconfig.jsonなどが含まれます (This includes pages, public, generated, next.config.js, tsconfig.json etc.)
COPY . .

# アプリケーションをビルド (Build the application)
RUN npm run build

# Next.jsが実行されるポートを公開 (Expose the port Next.js runs on)
EXPOSE 3000

# アプリケーションを本番モードで起動するコマンド (Command to start the application in production mode)
CMD ["npm", "start"]
