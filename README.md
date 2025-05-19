# Sayı Tahmin Oyunu 🎯

Modern arayüze sahip, ses efektleri ve animasyonlarla zenginleştirilmiş bir sayı tahmin oyunu. Python ve Tkinter kullanılarak geliştirilmiştir.

## Özellikler 🌟

- **3 farklı oyun modu:**
  - 👤 Tek Kişilik
  - 👥 İki Kişilik
  - 🤖 Bilgisayara Karşı
- 🎵 Arka plan müziği
- 🎨 Açık/Koyu tema desteği
- 🎮 Animasyonlu arayüz
- 🔊 Ses efektleri
- 📊 Detaylı tahmin geçmişi

## Kurulum 🔧

1. [Python](https://www.python.org/downloads/)'u indirin ve kurun (Python 3.6 veya üzeri).
2. Gerekli kütüphaneyi yükleyin:
   ```bash
   pip install pygame
   ```
3. Projeyi klonlayın:
   ```bash
   git clone <GitHub_Repo_URL>
   ```
4. Ses dosyalarını `sounds` klasörüne yerleştirin:
   - `background_music.mp3`
   - `button_click.mp3`
   - `correct.mp3`
   - `lose.mp3`
   - `win.mp3`
   - `wrong.mp3`

## Oynanış 🎮

1. Oyunu başlatın:
   ```bash
   python "Guessing Game.py"
   ```
2. Oyun modunu seçin.
3. 4 basamaklı bir sayıyı tahmin edin.

### 📌 Kurallar

- Her basamak farklı bir rakam olmalı.
- İlk basamak 0 olamaz.
- **✅ +1**: Doğru rakam, doğru yerde.
- **⚠️ -1**: Doğru rakam, yanlış yerde.
- **❌ 0**: Bu rakam sayıda yok.

## 💻 Sistem Gereksinimleri

- Python 3.6 veya üzeri
- `pygame` kütüphanesi
- Minimum 800x650 ekran çözünürlüğü
- Ses çıkışı (opsiyonel)
