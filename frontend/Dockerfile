# Użyj obrazu Node.js (pasującego do Twoich logów)
FROM node:20-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki package.json i package-lock.json
COPY package*.json ./

# Zainstaluj wszystkie zależności
RUN npm install

# Skopiuj resztę kodu źródłowego
COPY . .

# Wystaw port, na którym działa serwer deweloperski Vite
EXPOSE 5173

# Komenda startowa: uruchom serwer deweloperski Vite
# Flaga '--host' sprawia, że jest on dostępny z zewnątrz kontenera
CMD ["npm", "run", "dev", "--", "--host"]