# TODO - Plany i kolejne etapy prac

Ten plik zawiera propozycje kolejnych etapów prac nad projektem OptiRoute. Będzie on używany do planowania, priorytetyzacji i śledzenia postępu.

Format:
- [status] Tytuł (priorytet) — krótki opis

Statusy: [TODO], [IN-PROGRESS], [DONE]

---

## Priorytet Wysoki

- [DONE] Zaktualizować README i dodać plik TODO (wysokie) — Dodać dokumentację postępu prac i planów rozwoju.
- [DONE] Integracja z TomTom API (wysokie) — Implementacja optymalizacji tras i pobierania geometrii.
- [DONE] Wizualizacja tras (wysokie) — Interaktywna mapa z react-leaflet.
- [TODO] Testy jednostkowe (wysokie):
  - Upload Service: walidacja CSV, obsługa błędów
  - Optimization Service: geokodowanie, optymalizacja
  - Results Service: obsługa statusów, format odpowiedzi
  - Frontend: komponenty React, integracja API
- [TODO] Dokumentacja API (OpenAPI / Swagger) (wysokie):
  - Automatyczna generacja dokumentacji FastAPI
  - Przykłady użycia dla każdego endpointu
  - Opis schematów danych
- [TODO] Mechanizmy retry/timeout i obsługa błędów (wysokie):
  - Nominatim: rate limiting, cache
  - TomTom: obsługa błędów API, retry
  - RabbitMQ: dead letter queue
  - Frontend: obsługa timeout, wskaźniki postępu

## Priorytet Średni

- [TODO] Monitoring i metryki (średni):
  - Prometheus: metryki aplikacji (latencja, błędy)
  - Grafana: dashboardy dla każdego serwisu
  - RabbitMQ: monitorowanie kolejek i konsumentów
  - Postgres: statystyki zapytań i wydajność
- [TODO] Healthchecks i readiness/liveness (średni):
  - Endpointy health dla każdego serwisu
  - Integracja z Docker Compose healthcheck
  - Monitoring dostępności API zewnętrznych
- [TODO] Walidacja i skalowanie (średni):
  - Walidacja struktury i zawartości CSV
  - Chunking dla dużych plików
  - Wsparcie dla wielu formatów wejściowych
  - Rate limiting na poziomie Nginx

## Priorytet Niski

- [TODO] CI (GitHub Actions) (niski) — Uruchamianie testów, lint, budowanie obrazów Docker na PR.
- [TODO] Mocki zewnętrznych API dla testów (niski) — Stworzyć mocki TomTom/Nominatim/OpenWeatherMap/OpenAQ do testów integracyjnych.
- [TODO] Cache geokodowania (niski) — Lokalny cache dla często występujących adresów, by zaoszczędzić limity API.

## Pomysły długoterminowe

- Integracja z innymi dostawcami routingu (np. OSRM) jako alternatywa do TomTom.
- Interaktywne UI z możliwością edycji trasy i ręcznego przypisywania priorytetów dla przystanków.
- Optymalizacje kosztowe (koszty paliwa, uprawnienia kierowców, zmiany tras w czasie rzeczywistym).

---

Aby zaktualizować status zadania, edytuj odpowiednią linię zmieniając status na [IN-PROGRESS] lub [DONE] i dodaj krótką notkę z datą/komentarzem.
