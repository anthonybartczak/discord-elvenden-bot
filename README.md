# Elvie — WFRP 4e Discord Bot

**Elvie** to bot dla platformy Discord stworzony jako pomocnik do gry fabularnej **Warhammer Fantasy Roleplay (WFRP 4. edycja)** w języku polskim.

## ✨ Funkcjonalności

- **`/rozwinięcie`**: Precyzyjne kalkulowanie kosztu w Punktach Doświadczenia (PD) dla cech i umiejętności (z uwzględnieniem zniżek z talentów).
- **`/talent`**: Wyszukiwarka talentów z autouzupełnianiem (zwraca opis, testy i maksymalny poziom).
- **`/umiejętność`**: Wyszukiwarka umiejętności z autouzupełnianiem (typ, cecha bazowa, powiązane talenty).
- **`/błogosławieństwo`**: Przegląd błogosławieństw dla 10 bóstw WFRP 4e lub szczegółowe statystyki z autouzupełnianiem (zasięg, cel, czas trwania, efekt, bonusy za PS).
- **`/manifestacja`**: Losowanie mniejszych i większych manifestacji z oficjalnych tabel magii WFRP 4e.
- **`/spaczenie`**: Losowanie spaczenia fizycznego lub zepsucia psychicznego.
- **`/fortuna`**: Interaktywny mini-system losowania kart z użyciem przycisków Discord UI.
- **`/tabela_rozwinięć`**: Wyświetlanie tabeli kosztów PD (tekstowo na PC lub graficznie na urządzenia mobilne).
- **`/serwery`** & **`/zaproszenie`**: Informacje o bocie oraz szybki link zaproszenia.

---

## 🚀 Wymagania

- **Python 3.10+** (rekomendowany Python 3.11 / 3.12 / 3.13)
- Token bota Discord ([Discord Developer Portal](https://discord.com/developers/applications))

---

## 📦 Instalacja i uruchomienie

1. **Sklonuj repozytorium:**
   ```bash
   git clone https://github.com/anthonybartczak/discord-elvenden-bot.git
   cd discord-elvenden-bot
   ```

2. **Utwórz i aktywuj środowisko wirtualne (opcjonalnie, ale zalecane):**
   ```bash
   # Windows
   py -3 -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Skonfiguruj zmienne środowiskowe:**
   Stwórz `.env` i wklej swój token bota:
   ```bash
   cp .env.example .env
   ```
   Zawartość `.env`:
   ```env
   BOT_TOKEN=twoj_tajny_token_bota
   ```

5. **Uruchom bota:**
   ```bash
   python bot.py
   ```

---

## 📁 Struktura projektu

```text
├── content/
│   ├── abilities.json    # Baza umiejętności WFRP 4e
│   ├── blessings.json    # Baza błogosławieństw i kultów bóstw WFRP 4e
│   ├── talents.json      # Baza talentów WFRP 4e
│   ├── pictures.py       # Adresy zasobów graficznych (karty, awatary, tabele)
│   └── tables.py         # Tabele manifestacji, spaczeń i rozwinięć
├── .env.example          # Wzór konfiguracji środowiskowej
├── bot.py                # Główny kod bota i obsługa poleceń Slash
├── PRIVACY_POLICY.md     # Polityka prywatności (Privacy Policy)
├── TERMS_OF_SERVICE.md   # Regulamin korzystania (Terms of Service)
├── requirements.txt      # Główne zależności Python
└── README.md             # Dokumentacja projektu
```

---

## ⚖️ Warunki i Prywatność / Legal

- **[Polityka prywatności (Privacy Policy)](PRIVACY_POLICY.md)**
- **[Regulamin korzystania (Terms of Service)](TERMS_OF_SERVICE.md)**
- **[Licencja (MIT License)](LICENSE)**