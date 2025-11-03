# TODO - Plany i kolejne etapy prac

Ten plik zawiera propozycje kolejnych etapów prac nad projektem OptiRoute. Będzie on używany do planowania, priorytetyzacji i śledzenia postępu.

Format:
- [status] Tytuł (priorytet) — krótki opis

Statusy: [TODO], [IN-PROGRESS], [DONE]

---

## Priorytet Wysoki

- [IN-PROGRESS] Zaktualizować README i dodać plik TODO (wysokie) — Dodać dokumentację postępu prac i planów rozwoju.
- [TODO] Testy jednostkowe dla serwisów (wysokie) — Dodać pytest do każdego serwisu, pokryć krytyczne funkcje: geokodowanie, upload, results.
- [TODO] Dokumentacja API (OpenAPI / Swagger) (wysokie) — Dodać automatycznie generowane specyfikacje dla każdego serwisu REST.
- [TODO] Mechanizmy retry/timeout i obsługa błędów (wysokie) — Ulepszyć komunikację z zewnętrznymi API (TomTom, Nominatim, OpenWeatherMap) poprzez retry/backoff i timeouts.

## Priorytet Średni

- [TODO] Monitoring i metryki (Prometheus + Grafana) (średni) — Eksportować metryki z serwisów i RabbitMQ.
- [TODO] Healthchecks i readiness/liveness (średni) — Dodać endpointy health i konfigurację w Docker Compose / k8s.
- [TODO] Walidacja i skalowanie uploadu (średni) — Lepiej walidować CSV i wspierać większe pliki (chunking / stream processing).

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
