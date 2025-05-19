import tkinter as tk
from tkinter import ttk, messagebox
import random
import itertools
from typing import List, Tuple, Set, Dict, Optional, Any
import os
import sys
import time
import pygame  # Ses çalma için pygame kütüphanesi

class PPGGame:
    def __init__(self):
        # Ana pencere ayarları
        self.window = tk.Tk()
        self.window.title("🎯 Sayı Tahmin Oyunu 🎯")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Ses ayarları
        self.is_sound_on = True
        self.is_music_on = True
        self.sound_effects = {}
        
        try:
            if not pygame.get_init():
                pygame.init()
                
            if not pygame.mixer.get_init():
                print("Pygame mixer başlatılıyor...")
                pygame.mixer.quit()
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                print("Pygame mixer başlatıldı")
            
            pygame.mixer.set_num_channels(8)
            
            sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
            if not os.path.exists(sounds_dir):
                os.makedirs(sounds_dir)
                print(f"Ses dosyaları klasörü oluşturuldu: {sounds_dir}")
                print("Lütfen aşağıdaki ses dosyalarını bu klasöre ekleyin:")
                print("button_click.mp3, win.mp3, lose.mp3, correct.mp3, wrong.mp3, background_music.mp3")
            
            print("Ses dosyaları yükleniyor...")
            sound_files = {
                'button_click': "button_click.mp3",
                'win': "win.mp3", 
                'lose': "lose.mp3",
                'correct': "correct.mp3", 
                'wrong': "wrong.mp3",
                'background': "background_music.mp3"
            }
            

            for sound_name, file_name in sound_files.items():
                sound_obj = self.load_sound(file_name)
                if sound_obj:
                    print(f"{file_name} başarıyla yüklendi.")
                else:
                    print(f"UYARI: {file_name} yüklenemedi veya bulunamadı!")
                self.sound_effects[sound_name] = sound_obj
                
        except Exception as e:
            print(f"Ses sistemi başlatılırken hata: {e}")
       
            self.is_sound_on = False
            self.is_music_on = False
         
            import traceback
            traceback.print_exc()
        
        # Tema durumu
        self.is_dark_mode = True
        
        # Ses ayarları
        self.is_sound_on = True
        self.is_music_on = True
        
        # Tema renkleri
        self.dark_theme = {
            'bg_dark': '#1a1a2e',      # Koyu lacivert
            'bg_medium': '#16213e',    # Orta lacivert
            'bg_light': '#0f3460',     # Açık lacivert
            'accent': '#ff6b6b',       # Mercan kırmızısı
            'success': '#4ecdc4',      # Turkuaz
            'warning': '#ffe66d',      # Sarı
            'info': '#74b9ff',         # Mavi
            'white': '#ffffff',        # Beyaz
            'text_light': '#ecf0f1',   # Açık gri
            'text_dark': '#2c3e50',    # Koyu gri
            'text_primary': '#ffffff'  # Beyaz
        }
        
        self.light_theme = {
            'bg_dark': '#f8f9fa',      # Çok açık gri
            'bg_medium': '#e9ecef',    # Açık gri
            'bg_light': '#ffffff',     # Beyaz
            'accent': '#e74c3c',       # Kırmızı
            'success': '#27ae60',      # Yeşil
            'warning': '#f39c12',      # Turuncu
            'info': '#3498db',         # Mavi
            'white': '#2d3436',        # Koyu gri
            'text_light': '#34495e',   # Lacivert
            'text_dark': '#2c3e50',    # Koyu lacivert
            'text_primary': '#2c3e50', # Koyu lacivert
            'text_input': '#1e272e'    # Çok koyu gri
        }
        

        self.colors = self.dark_theme if self.is_dark_mode else self.light_theme
        

        self.window.configure(bg=self.colors['bg_dark'])
        
        # Oyun durumu
        self.secret_number = ""
        self.current_player = 1
        self.player1_attempts = []
        self.player2_attempts = []
        self.max_attempts = 10
        self.game_mode = None
        self.current_interface = "main_menu"
        self.computer_possible_numbers = set()
        self.computer_attempts = []
        self.cpu_guess_number = ""
        
        self.animation_running = False
        
        self.window.minsize(800, 650)
        
        self.window.pack_propagate(False)
        
        self.play_background_music()
        
        self.create_main_menu()
        
    def create_gradient_frame(self, parent, color1, color2, height=None):
        """Gradient efekti oluşturur"""
        frame = tk.Frame(parent, bg=color1)
        if height:
            frame.configure(height=height)
        return frame
        
    def create_rounded_button(self, parent, text, command, bg_color, hover_color=None, **kwargs):
        """Yuvarlatılmış kenarlı buton oluşturur"""
        if hover_color is None:
            hover_color = bg_color
            
        # Font parametresi kwargs içinde değilse varsayılan değeri kullan
        if 'font' not in kwargs:
            kwargs['font'] = ('Roboto', 12, 'bold')
            
        button = tk.Button(parent, text=text, command=command, 
                        bg=bg_color, fg=self.colors['white'],
                        relief='flat', borderwidth=0,
                        padx=30, pady=15,
                        cursor='hand2',
                        **kwargs)
        
        # Hover efekti
        def on_enter(e):
            button.configure(bg=hover_color)
        def on_leave(e):
            button.configure(bg=bg_color)
            
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def create_animated_label(self, parent, text, **kwargs):
        """Animasyonlu label oluşturur"""
        label = tk.Label(parent, text=text, **kwargs)
        
        self.animate_fade_in(label)
        return label
    
    def animate_fade_in(self, widget):
        """Widget için fade-in animasyonu"""
        def fade_step(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.1
                widget.after(50, lambda: fade_step(alpha))
        fade_step()
    
    def create_main_menu(self):
        for widget in self.window.winfo_children():
            widget.destroy()
            
        self.current_interface = "main_menu"
        self.game_mode = None
        
        main_container = tk.Frame(self.window, bg=self.colors['bg_dark'])
        main_container.pack(expand=True, fill='both')

        content_container = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content_container.pack(expand=True, fill='both', padx=30, pady=20)
        
        top_menu = tk.Frame(content_container, bg=self.colors['bg_dark'])
        top_menu.pack(fill='x', anchor='ne')
        
        music_icon = "🎵" if self.is_music_on else "🎵🚫"
        music_button = tk.Button(
            top_menu,
            text=music_icon,
            command=self.toggle_music,
            font=('Roboto', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        music_button.pack(side='right', padx=5)
        
        # Tema değiştirme butonu
        theme_icon = "🌞" if self.is_dark_mode else "🌙"
        theme_button = tk.Button(
            top_menu,
            text=theme_icon,
            command=self.toggle_theme,
            font=('Roboto', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        theme_button.pack(side='right', padx=5)

        # Başlık container
        title_container = tk.Frame(content_container, bg=self.colors['bg_dark'])
        title_container.pack(pady=(20, 30))
        
        # Ana başlık - büyük ve renkli
        title_label = tk.Label(
            title_container, 
            text="🎯", 
            font=('Arial Black', 48, 'bold'), 
            bg=self.colors['bg_dark'], 
            fg=self.colors['accent']
        )
        title_label.pack()
        
        # Başlık animasyonu
        self.title_size = 48  # Başlangıç boyutu
        self.size_increasing = True
        
        def pulse_title():
            if self.size_increasing:
                self.title_size += 2
                if self.title_size >= 54:
                    self.size_increasing = False
            else:
                self.title_size -= 2
                if self.title_size <= 48:
                    self.size_increasing = True
            
            title_label.configure(font=('Arial Black', self.title_size, 'bold'))
            title_label.after(500, pulse_title)
        
        pulse_title()
        
        # Alt başlık
        subtitle_label = tk.Label(
            title_container,
            text="Sayı Tahmin Oyunu",
            font=('Roboto', 24, 'normal'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_light']
        )
        subtitle_label.pack(pady=(0, 5))
        
        # Dekoratif çizgi
        line_frame = tk.Frame(title_container, bg=self.colors['accent'], height=3, width=200)
        line_frame.pack(pady=5)
        
        # Açıklama container - arkaplan ile aynı renk
        desc_container = tk.Frame(content_container, bg=self.colors['bg_dark'], relief='flat')
        desc_container.pack(pady=(0, 10), ipady=5, padx=80)  # Padding daha da azaltıldı
    
        # Açıklama metni
        desc_lines = [
            "🎲 4 farklı rakamdan oluşan gizli sayıyı tahmin edin!",
            "",
            "📋 KURALLAR:",
            "• Her basamak farklı bir rakam olmalı",
            "• İlk basamak 0 olamaz",
            "• ✅ +1: Doğru rakam, doğru yerde",
            "• ⚠️ -1: Doğru rakam, yanlış yerde",
            "• ❌ 0: Bu rakam sayıda yok"
        ]
        
        for line in desc_lines:
            color = self.colors['accent'] if line.startswith("📋") else self.colors['text_light']
            font_weight = 'bold' if line.startswith("📋") else 'normal'
            
            tk.Label(desc_container, text=line,
                    font=('Roboto', 12, font_weight),
                    bg=self.colors['bg_dark'],  # Arkaplan rengi ayarlandı
                    fg=color).pack(pady=2)
    
        # Oyun modu butonları için ana container
        modes_container = tk.Frame(content_container, bg=self.colors['bg_dark'])
        modes_container.pack(expand=True, fill='both', padx=80)  # Kurallar bölümüyle aynı genişlikte
    
        # Buton bilgileri
        buttons_info = [
            ("👤 Tek Kişilik Oyun", self.start_single_player, self.colors['info']),
            ("👥 İki Kişilik Oyun", self.start_two_player, self.colors['accent']),
            ("🤖 Bilgisayara Karşı", self.start_vs_computer, self.colors['warning'])
        ]
        
        # Her buton için
        for text, command, color in buttons_info:
            # Buton container
            btn_container = tk.Frame(modes_container, bg=self.colors['bg_dark'])
            btn_container.pack(pady=4, fill='x')  # Düşey boşluk azaltıldı
            
            # Buton
            btn = tk.Button(
                btn_container,
                text=text,
                command=lambda cmd=command: self.animate_button_click(cmd),
                font=('Roboto', 12, 'bold'),
                bg=color,
                fg=self.colors['white'],
                relief='flat',
                borderwidth=0,
                padx=10,
                pady=10,
                cursor='hand2',
                width=15
            )
            btn.pack(expand=True)
            
            # Hover efekti
            def on_enter(e, button=btn, orig_color=color):
                button.configure(bg=self.adjust_color(orig_color, 20))
                
            def on_leave(e, button=btn, orig_color=color):
                button.configure(bg=orig_color)
                
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
        
        # Alt boşluk - azaltıldı
        tk.Frame(content_container, height=10, bg=self.colors['bg_dark']).pack()
    
    def animate_button_click(self, command):
        """Buton tıklama animasyonu ve sonrasında komutu çalıştırır"""
        # Her zaman ses çal (sound_on False olsa bile)
        try:
            if self.sound_effects.get("button_click"):
                # Özel kanalda çal
                channel = pygame.mixer.Channel(2)  # 3. kanal
                channel.set_volume(0.7)
                channel.play(self.sound_effects["button_click"])
        except Exception as e:
            print(f"Buton sesi çalma hatası: {e}")
        
        # Komutu çalıştır
        command()
    
    def generate_secret_number(self):
        """4 farklı basamaklı gizli sayı üretir"""
        first_digit = random.randint(1, 9)
        remaining_digits = [i for i in range(10) if i != first_digit]
        selected_digits = random.sample(remaining_digits, 3)
        return str(first_digit) + ''.join(map(str, selected_digits))
    
    def validate_guess(self, guess: str) -> Tuple[bool, str]:
        """Tahmin geçerliliğini kontrol eder"""
        if len(guess) != 4:
            return False, "🔢 Tahmin 4 basamaklı olmalı!"
        
        if not guess.isdigit():
            return False, "🔤 Sadece rakam giriniz!"
        
        if guess[0] == '0':
            return False, "🚫 İlk basamak 0 olamaz!"
        
        if len(set(guess)) != 4:
            return False, "🔄 Tüm basamaklar farklı olmalı!"
        
        return True, ""
    
    def calculate_feedback(self, secret: str, guess: str) -> List[int]:
        """Geri bildirim hesaplar"""
        feedback = []
        
        for i, digit in enumerate(guess):
            if digit == secret[i]:
                feedback.append(1)  # Doğru yerde
            elif digit in secret:
                feedback.append(-1) # Yanlış yerde
            else:
                feedback.append(0)  # Yok
        
        return feedback
    
    def start_single_player(self):
        self.game_mode = "single"
        self.secret_number = self.generate_secret_number()
        self.player1_attempts = []
        self.create_game_interface()
    
    def start_two_player(self):
        self.game_mode = "two_player"
        self.secret_number = self.generate_secret_number()
        self.current_player = 1
        self.player1_attempts = []
        self.player2_attempts = []
        self.create_game_interface()
    
    def start_vs_computer(self):
        self.game_mode = "vs_computer"
        self.secret_number = self.generate_secret_number()
        self.player1_attempts = []
        self.computer_attempts = []
        self.computer_possible_numbers = self.generate_all_possible_numbers()
        self.create_game_interface()
    
    def generate_all_possible_numbers(self) -> Set[str]:
        """Bilgisayar için tüm olası sayıları üretir"""
        possible = set()
        for first in range(1, 10):
            for rest in itertools.permutations(range(10), 3):
                if first not in rest:
                    number = str(first) + ''.join(map(str, rest))
                    possible.add(number)
        return possible
    
    def computer_make_guess(self):
        """Bilgisayarın tahmin yapması"""
        # vs_computer modunda bilgisayar tahmini
        if self.game_mode == "vs_computer":
            # Bilgisayar için yeni bir tahmin oluştur
            if not self.computer_possible_numbers:
                self.computer_possible_numbers = self.generate_all_possible_numbers()
                
            # Eğer olası tahminler varsa filtreleme yap
            if self.computer_attempts:
                filtered = set()
                for candidate in self.computer_possible_numbers:
                    is_valid = True
                    for attempt, fb in self.computer_attempts:
                        if self.calculate_feedback(candidate, attempt) != fb:
                            is_valid = False
                            break
                    if is_valid:
                        filtered.add(candidate)
                
                self.computer_possible_numbers = filtered
            
            # Yeni tahmin yap
            if not self.computer_possible_numbers:
                next_guess = self.generate_secret_number()
            else:
                next_guess = random.choice(list(self.computer_possible_numbers))
            
            return next_guess
            
        # user_vs_cpu modu için eski kod (artık kullanılmıyor)
        if self.game_mode != "user_vs_cpu":
            return
        
        # Arayüzden geri bildirimleri al
        feedback = [var.get() for var in self.feedback_vars]
        
        # İlk tahmin değilse, önceki tahmini ve geri bildirimi kaydet
        if self.computer_attempts:
            prev_guess = self.cpu_guess_entry.get().strip()
            self.computer_attempts.append((prev_guess, feedback))
            
            # Ses efekti
            if sum(feedback) == 4:
                self.play_sound("lose")
            elif sum(feedback) > 0:
                self.play_sound("correct")
            else:
                self.play_sound("wrong")
            
            # Kazanma kontrolü
            if sum(feedback) == 4:
                self.show_game_end_popup(
                    f"😢 KAYBETTİNİZ!\n\n"
                    f"Bilgisayar {len(self.computer_attempts)} tahminde bildi!\n\n"
                    f"Bilgisayarın Gizli Sayısı: {self.cpu_guess_number}"
                )
                return
            
            # Hak kontrolü
            if len(self.computer_attempts) >= self.max_attempts:
                self.show_game_end_popup(
                    f"🎉 Tebrikler! Bilgisayar bulamadı!\n\n"
                    f"Bilgisayarın Gizli Sayısı: {self.cpu_guess_number}"
                )
                return
        
        # Olası sayıları filtrele
        if self.computer_attempts:
            filtered = set()
            for candidate in self.computer_possible_numbers:
                is_valid = True
                for attempt, fb in self.computer_attempts:
                    if self.calculate_feedback(candidate, attempt) != fb:
                        is_valid = False
                        break
                if is_valid:
                    filtered.add(candidate)
            
            self.computer_possible_numbers = filtered
        
        # Yeni tahmin yap
        if not self.computer_possible_numbers:
            # Eğer olası sayı kalmadıysa (hatalı geri bildirim girildiğinde)
            next_guess = self.generate_secret_number()
        else:
            next_guess = random.choice(list(self.computer_possible_numbers))
        
        # Bilgisayar tahmini göster
        self.cpu_guess_entry.delete(0, 'end')
        self.cpu_guess_entry.insert(0, next_guess)
        
        # Geri bildirim seçeneklerini sıfırla
        for var in self.feedback_vars:
            var.set(0)
        
        # Bilgisayar kalan hakları güncelle
        cpu_attempts_left = self.max_attempts - len(self.computer_attempts)
        self.cpu_attempts_label.config(text=f"Bilgisayar kalan hakkı: {cpu_attempts_left}")
        
        # Tahmin geçmişini güncelle
        self.update_user_vs_cpu_history()
        
        return next_guess
    
    def create_game_interface(self):
        # Pencereyi temizle
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Mevcut arayüzü oyun arayüzü olarak ayarla
        self.current_interface = "game_interface"
        
        # Ana container
        main_container = tk.Frame(self.window, bg=self.colors['bg_dark'])
        main_container.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Üst başlık
        header_frame = tk.Frame(main_container, bg=self.colors['bg_medium'], height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Başlık container
        title_container = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        title_container.pack(expand=True, fill='both', padx=20)
        
        # Tema değiştirme butonu (sağ)
        theme_icon = "🌞" if self.is_dark_mode else "🌙"
        theme_button = tk.Button(
            title_container,
            text=theme_icon,
            command=self.toggle_theme,
            font=('Roboto', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        theme_button.pack(side='right', padx=5, pady=5)
        
        # Müzik açma/kapama butonu
        music_icon = "🎵" if self.is_music_on else "🎵🚫"
        music_button = tk.Button(
            title_container,
            text=music_icon,
            command=self.toggle_music,
            font=('Roboto', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        music_button.pack(side='right', padx=5, pady=5)
        
        # Oyun modu başlığı
        mode_emojis = {
            "single": "👤",
            "two_player": "👥", 
            "vs_computer": "🤖"
        }
        
        mode_texts = {
            "single": "Tek Kişilik Oyun",
            "two_player": "İki Kişilik Oyun",
            "vs_computer": "Oyuncu vs Bilgisayar"
        }
        
        emoji = mode_emojis[self.game_mode]
        title_text = f"{emoji} {mode_texts[self.game_mode]}"
        
        title_label = tk.Label(title_container, text=title_text,
                              font=('Roboto', 20, 'bold'),
                              bg=self.colors['bg_medium'],
                              fg=self.colors['accent'])
        title_label.pack(side='left', expand=True)
        
        # İçerik alanı
        content_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content_frame.pack(expand=True, fill='both')
        
        # Sol panel - Tahmin girişi
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_medium'], width=400)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Üst boşluk
        tk.Frame(left_panel, bg=self.colors['bg_medium'], height=20).pack()
        
        # Mevcut oyuncu bilgisi - daha büyük ve renkli
        if self.game_mode == "two_player":
            player_colors = [self.colors['info'], self.colors['accent']]
            color = player_colors[self.current_player - 1]
            self.current_player_label = tk.Label(
                left_panel,
                text=f"🎯 Oyuncu {self.current_player}'in Sırası",
                font=('Roboto', 16, 'bold'),
                bg=self.colors['bg_medium'],
                fg=color
            )
            self.current_player_label.pack(pady=20)
        elif self.game_mode == "vs_computer":
            self.current_player_label = tk.Label(
                left_panel,
                text="🎮 Oyuncu Sırası",
                font=('Roboto', 16, 'bold'),
                bg=self.colors['bg_medium'],
                fg=self.colors['info']
            )
            self.current_player_label.pack(pady=20)
        
        # Tahmin input container
        input_container = tk.Frame(left_panel, bg=self.colors['bg_light'])
        input_container.pack(pady=20, padx=30, fill='x')
        
        # Tahmin etiketi
        tk.Label(input_container, text="🎲 Tahmininizi Girin:",
                font=('Roboto', 14, 'bold'),
                bg=self.colors['bg_light'],
                fg=self.colors['white']).pack(pady=(15, 10))
        
        # Tahmin giriş alanı - daha büyük ve renkli
        self.guess_entry = tk.Entry(input_container,
                                   font=('Roboto', 18, 'bold'),
                                   width=8,
                                   justify='center',
                                   bg=self.colors['bg_medium'],
                                   fg=self.colors['white'],
                                   relief='flat',
                                   bd=5)
        self.guess_entry.pack(pady=10)
        
        # Tahmin butonu - daha büyük
        self.guess_button = self.create_rounded_button(
            input_container,
            "🎯 TAHMIN ET",
            self.make_guess,
            self.colors['success'],
            font=('Roboto', 14, 'bold'),
            width=15
        )
        self.guess_button.pack(pady=(10, 15))
        
        # Bilgisayar otomatik tahmin yapar, buton kaldırıldı
        
        # Alt bilgiler
        info_frame = tk.Frame(left_panel, bg=self.colors['bg_light'])
        info_frame.pack(fill='x', padx=30, pady=20)
        
        # Kalan hak göstergesi
        if self.game_mode == "single":
            remaining = self.max_attempts - len(self.player1_attempts)
        elif self.game_mode == "vs_computer":
            remaining = self.max_attempts - len(self.player1_attempts)
        else:
            total_attempts = len(self.player1_attempts) + len(self.player2_attempts)
            remaining = (self.max_attempts * 2) - total_attempts
        
        self.remaining_label = tk.Label(info_frame, text=f"💎 Kalan Hak: {remaining}",
                font=('Roboto', 12, 'bold'),
                bg=self.colors['bg_light'],
                fg=self.colors['warning'])
        self.remaining_label.pack(pady=5)
        
        # Geri dönüş butonu
        tk.Frame(left_panel, bg=self.colors['bg_medium'], height=20).pack()
        back_button = self.create_rounded_button(
            left_panel,
            "🏠 ANA MENÜ",
            self.create_main_menu,
            '#7f8c8d',
            font=('Roboto', 12, 'bold'),
            width=15
        )
        back_button.pack(pady=10)
        
        # Sağ panel - Tahmin geçmişi
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Geçmiş başlığı
        history_header = tk.Frame(right_panel, bg=self.colors['bg_light'], height=60)
        history_header.pack(fill='x')
        history_header.pack_propagate(False)
        
        tk.Label(history_header, text="📊 TAHMİN GEÇMİŞİ",
                font=('Roboto', 16, 'bold'),
                bg=self.colors['bg_light'],
                fg=self.colors['text_light']).pack(expand=True)
        
        # Scrollable geçmiş
        canvas = tk.Canvas(right_panel, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        self.history_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        self.history_frame.bind("<Configure>",
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Fare tekerleği desteği
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Enter tuşu ile tahmin
        self.guess_entry.bind('<Return>', lambda e: self.make_guess())
        self.guess_entry.focus()
        
        # İlk geçmişi göster
        self.update_history_display()
    
    def make_guess(self):
        """Oyuncu tahmin yapar"""
        guess = self.guess_entry.get().strip()
        
        # Tahmin geçerliliğini kontrol et
        is_valid, error_msg = self.validate_guess(guess)
        if not is_valid:
            self.show_error_popup(error_msg)
            return
        
        # Geri bildirim hesapla
        feedback = self.calculate_feedback(self.secret_number, guess)
        
        # Tahmin geçmişine ekle
        if self.game_mode == "single":
            self.player1_attempts.append((guess, feedback))
        elif self.game_mode == "two_player":
            if self.current_player == 1:
                self.player1_attempts.append((guess, feedback))
            else:
                self.player2_attempts.append((guess, feedback))
        elif self.game_mode == "vs_computer":
            self.player1_attempts.append((guess, feedback))
        
        # Giriş alanını temizle ve animasyon
        self.animate_guess_submission()
        
        # Oyun bitimi kontrolü
        if sum(feedback) == 4:
            self.window.after(500, self.game_won)
            return
        
        # Hak kontrolü
        if self.game_mode == "single":
            if len(self.player1_attempts) >= self.max_attempts:
                self.window.after(500, self.game_lost)
                return
        elif self.game_mode == "two_player":
            # İki kişilik oyunda sırayı değiştir
            self.current_player = 2 if self.current_player == 1 else 1
            player_colors = [self.colors['info'], self.colors['accent']]
            color = player_colors[self.current_player - 1]
            self.current_player_label.config(
                text=f"🎯 Oyuncu {self.current_player}'in Sırası",
                fg=color
            )
            
            total_attempts = len(self.player1_attempts) + len(self.player2_attempts)
            if total_attempts >= self.max_attempts * 2:
                self.window.after(500, self.game_lost)
                return
        elif self.game_mode == "vs_computer":
            if len(self.player1_attempts) >= self.max_attempts:
                self.window.after(500, self.game_lost)
                return
            
            # Oyuncu tahmin yaptıktan sonra bilgisayarın da tahmin yapmasını sağla
            self.window.after(500, self.computer_guess)
        
        # Geçmişi güncelle
        self.update_history_display()
        
        # Kalan hak güncelle
        self.update_remaining_attempts()
    
    def animate_guess_submission(self):
        """Tahmin gönderme animasyonu"""
        self.guess_entry.delete(0, tk.END)
        original_bg = self.guess_button.cget('bg')
        
        # Buton renk animasyonu
        self.guess_button.configure(bg=self.colors['warning'])
        self.window.after(200, lambda: self.guess_button.configure(bg=original_bg))
    
    def update_remaining_attempts(self):
        """Kalan hak sayısını günceller"""
        if self.game_mode == "single":
            remaining = self.max_attempts - len(self.player1_attempts)
        elif self.game_mode == "vs_computer":
            remaining = self.max_attempts - len(self.player1_attempts)
        else:
            total_attempts = len(self.player1_attempts) + len(self.player2_attempts)
            remaining = (self.max_attempts * 2) - total_attempts
        if hasattr(self, 'remaining_label') and self.remaining_label:
            self.remaining_label.config(text=f"💎 Kalan Hak: {remaining}")
    
    def show_error_popup(self, message):
        """Hata mesajı popup'ı"""
        error_window = tk.Toplevel(self.window)
        error_window.title("❌ Hata")
        error_window.geometry("400x200")
        error_window.configure(bg=self.colors['bg_dark'])
        error_window.resizable(False, False)
        
        # Pencereyi ortala
        error_window.transient(self.window)
        error_window.grab_set()
        
        # İçerik
        tk.Label(error_window, text="❌", font=('Arial', 48),
                bg=self.colors['bg_dark'], fg=self.colors['accent']).pack(pady=20)
        
        tk.Label(error_window, text=message, font=('Roboto', 12),
                bg=self.colors['bg_dark'], fg=self.colors['text_light'],
                wraplength=350).pack(pady=10)
        
        self.create_rounded_button(error_window, "TAMAM", error_window.destroy,
                                  self.colors['accent']).pack(pady=20)
    
    def toggle_theme(self):
        """Temayı değiştirir"""
        self.is_dark_mode = not self.is_dark_mode
        self.colors = self.dark_theme if self.is_dark_mode else self.light_theme
        
        # Temayı değiştirme animasyonu
        self.animate_theme_change()
        
        # Tüm pencereyi güncelle
        self.window.configure(bg=self.colors['bg_dark'])
        
        # Mevcut widget'ları temizle
        for widget in self.window.winfo_children():
            widget.destroy()
            
        # Mevcut arayüzü yeniden yükle
        if self.current_interface == "game_interface":
            # Oyun içinde ise oyun arayüzünü yeniden yükle
            self.create_game_interface()
        elif self.current_interface == "main_menu":
            # Ana menüde ise ana menüyü yükle
            self.create_main_menu()
        elif self.current_interface == "user_vs_cpu_interface":
            # Kullanıcı vs Bilgisayar modunda ise o arayüzü yükle
            self.create_user_vs_cpu_interface()
    
    def animate_theme_change(self):
        """Tema değişimi animasyonu"""
        # Ekrana geçici bir overlay ekle
        overlay = tk.Toplevel(self.window)
        overlay.overrideredirect(True)  # Başlık çubuğunu gizle
        
        # Overlay'ı pencere büyüklüğünde yap
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = self.window.winfo_rootx()
        y = self.window.winfo_rooty()
        overlay.geometry(f"{w}x{h}+{x}+{y}")
        
        # Overlay içeriği
        overlay_frame = tk.Frame(overlay, bg=self.colors['bg_dark'])
        overlay_frame.pack(fill='both', expand=True)
        
        icon = "🌞" if self.is_dark_mode else "🌙"
        label = tk.Label(overlay_frame, text=icon, font=('Arial', 48),
                        bg=self.colors['bg_dark'], fg=self.colors['accent'])
        label.pack(expand=True)
        
        # 0.5 saniye sonra kapat
        overlay.after(500, overlay.destroy)
    
    def start_user_vs_cpu(self):
        """Kullanıcı vs Bilgisayar modunu başlatır"""
        self.game_mode = "user_vs_cpu"
        # Bilgisayarın tahmin edeceği sayıyı oluştur
        self.cpu_guess_number = self.generate_secret_number()
        # Kullanıcı ve bilgisayar tahminlerini sıfırla
        self.player1_attempts = []
        self.computer_attempts = []
        self.computer_possible_numbers = self.generate_all_possible_numbers()
        # Arayüzü oluştur
        self.create_user_vs_cpu_interface()
    
    def update_window_theme(self):
        """Pencere temasını günceller"""
        # Renkleri güncelle
        self.window.configure(bg=self.colors['bg_dark'])
        
        for widget in self.window.winfo_children():
            widget.configure(bg=self.colors['bg_dark'])
            if isinstance(widget, tk.Label):
                widget.configure(fg=self.colors['text_primary'])
            
        # Geçmişi güncelle
        self.update_history_display()
    
    def execute_computer_guess(self):
        """Bilgisayar tahminini gerçekleştirir"""
        if self.game_mode != "vs_computer":
            return
            
        # Bilgisayar için tahmin oluştur
        computer_guess = self.computer_make_guess()
        if computer_guess is None:  # Eğer tahmin oluşturulamadıysa
            computer_guess = self.generate_secret_number()  # Rastgele bir tahmin yap
        
        # Tahmin için geri bildirim hesapla
        feedback = self.calculate_feedback(self.secret_number, computer_guess)
        
        # Tahmin geçmişine ekle
        self.computer_attempts.append((computer_guess, feedback))
        
        # Oyun bitimi kontrolü
        if sum(feedback) == 4:
            self.show_game_end_popup(
                f"🤖 Bilgisayar Kazandı! 🏆\n\n"
                f"Gizli Sayı: {self.secret_number}\n"
                f"Bilgisayar {len(self.computer_attempts)} tahminde buldu!"
            )
            return
        
        # Hak kontrolü
        if len(self.computer_attempts) >= self.max_attempts:
            self.show_game_end_popup(
                f"🤝 Berabere! \n\n"
                f"Bilgisayar da bulamadı!\n"
                f"Gizli Sayı: {self.secret_number}"
            )
            return
        
        # Geçmişi güncelle
        self.update_history_display()
    
    def format_feedback(self, feedback: List[int]) -> str:
        """Geri bildirimi formatlar"""
        positive = sum(1 for f in feedback if f == 1)
        negative = sum(1 for f in feedback if f == -1)
        if positive == 0 and negative == 0:
            return "💔 0"
        result = []
        if positive > 0:
            result.append(f"✅ +{positive}")
        if negative > 0:
            result.append(f"⚠️ -{negative}")
        return " ".join(result)
    
    def update_history_display(self):
        """Tahmin geçmişini günceller"""
        # Geçmiş frame'i temizle
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        if self.game_mode == "single":
            self.display_player_history("🎮 Tahminleriniz", self.player1_attempts, self.colors['info'])
        elif self.game_mode == "two_player":
            self.display_player_history("👤 Oyuncu 1", self.player1_attempts, self.colors['info'])
            if self.player2_attempts:
                tk.Frame(self.history_frame, bg=self.colors['bg_medium'], height=20).pack()
            self.display_player_history("👤 Oyuncu 2", self.player2_attempts, self.colors['accent'])
        elif self.game_mode == "vs_computer":
            # İki panel yan yana görüntülenecek
            history_row = tk.Frame(self.history_frame, bg=self.colors['bg_medium'])
            history_row.pack(fill='both', expand=True)
            
            # Sol panel - Kullanıcı tahminleri
            user_panel = tk.Frame(history_row, bg=self.colors['bg_medium'])
            user_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
            
            # Sol panel başlık
            user_title_frame = tk.Frame(user_panel, bg=self.colors['bg_light'])
            user_title_frame.pack(fill='x', pady=(5, 10))
            
            tk.Label(user_title_frame, text="🎮 Sizin Tahminleriniz", 
                   font=('Roboto', 12, 'bold'),
                   bg=self.colors['bg_light'], 
                   fg=self.colors['info'],
                   pady=5).pack()
            
            # Kullanıcı tahminleri içeriği
            if self.player1_attempts:
                for i, (guess, feedback) in enumerate(reversed(self.player1_attempts)):
                    attempt_num = len(self.player1_attempts) - i
                    
                    # Her tahmin için container
                    attempt_frame = tk.Frame(user_panel, bg=self.colors['bg_light'], relief='flat', bd=1)
                    attempt_frame.pack(fill='x', pady=2)
                    
                    # İç frame
                    inner_frame = tk.Frame(attempt_frame, bg=self.colors['bg_light'])
                    inner_frame.pack(fill='x', padx=10, pady=5)
                    
                    # Tahmin numarası ve sayısı
                    num_label = tk.Label(inner_frame, text=f"#{attempt_num}", 
                                        font=('Roboto', 10, 'bold'),
                                        bg=self.colors['bg_light'], 
                                        fg=self.colors['info'])
                    num_label.pack(side='left')
                    
                    guess_label = tk.Label(inner_frame, text=guess, 
                                          font=('Consolas', 14, 'bold'),
                                          bg=self.colors['bg_light'], 
                                          fg=self.colors['white'])
                    guess_label.pack(side='left', padx=(5, 0))
                    
                    # Geri bildirim
                    feedback_str = self.format_feedback(feedback)
                    feedback_label = tk.Label(inner_frame, text=feedback_str, 
                                             font=('Roboto', 10, 'bold'),
                                             bg=self.colors['bg_light'], 
                                             fg=self.colors['info'])
                    feedback_label.pack(side='right')
                    
                    # Kazanma durumu
                    if sum(feedback) == 4:
                        attempt_frame.configure(bg=self.colors['success'])
                        inner_frame.configure(bg=self.colors['success'])
                        for widget in [num_label, guess_label, feedback_label]:
                            widget.configure(bg=self.colors['success'])
            
            # Sağ panel - Bilgisayar tahminleri
            comp_panel = tk.Frame(history_row, bg=self.colors['bg_medium'])
            comp_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))
            
            # Sağ panel başlık
            comp_title_frame = tk.Frame(comp_panel, bg=self.colors['bg_light'])
            comp_title_frame.pack(fill='x', pady=(5, 10))
            
            tk.Label(comp_title_frame, text="🤖 Bilgisayar Tahminleri", 
                   font=('Roboto', 12, 'bold'),
                   bg=self.colors['bg_light'], 
                   fg=self.colors['warning'],
                   pady=5).pack()
            
            # Bilgisayar tahminleri içeriği
            if self.computer_attempts:
                for i, (guess, feedback) in enumerate(reversed(self.computer_attempts)):
                    attempt_num = len(self.computer_attempts) - i
                    
                    # Her tahmin için container
                    attempt_frame = tk.Frame(comp_panel, bg=self.colors['bg_light'], relief='flat', bd=1)
                    attempt_frame.pack(fill='x', pady=2)
                    
                    # İç frame
                    inner_frame = tk.Frame(attempt_frame, bg=self.colors['bg_light'])
                    inner_frame.pack(fill='x', padx=10, pady=5)
                    
                    # Tahmin numarası ve sayısı
                    num_label = tk.Label(inner_frame, text=f"#{attempt_num}", 
                                        font=('Roboto', 10, 'bold'),
                                        bg=self.colors['bg_light'], 
                                        fg=self.colors['warning'])
                    num_label.pack(side='left')
                    
                    guess_label = tk.Label(inner_frame, text=guess, 
                                          font=('Consolas', 14, 'bold'),
                                          bg=self.colors['bg_light'], 
                                          fg=self.colors['white'])
                    guess_label.pack(side='left', padx=(5, 0))
                    
                    # Geri bildirim
                    feedback_str = self.format_feedback(feedback)
                    feedback_label = tk.Label(inner_frame, text=feedback_str, 
                                             font=('Roboto', 10, 'bold'),
                                             bg=self.colors['bg_light'], 
                                             fg=self.colors['warning'])
                    feedback_label.pack(side='right')
                    
                    # Kazanma durumu
                    if sum(feedback) == 4:
                        attempt_frame.configure(bg=self.colors['success'])
                        inner_frame.configure(bg=self.colors['success'])
                        for widget in [num_label, guess_label, feedback_label]:
                            widget.configure(bg=self.colors['success'])
    
    def display_player_history(self, title: str, attempts: List[Tuple[str, List[int]]], color: str):
        """Bir oyuncunun tahmin geçmişini görüntüler"""
        if not attempts:
            return
            
        # Başlık container
        title_container = tk.Frame(self.history_frame, bg=self.colors['bg_light'])
        title_container.pack(fill='x', padx=10, pady=(10, 5))
        
        tk.Label(title_container, text=title, font=('Roboto', 14, 'bold'), 
                 bg=self.colors['bg_light'], fg=color,
                 pady=10).pack()
        
        # Tahminler container
        attempts_container = tk.Frame(self.history_frame, bg=self.colors['bg_medium'])
        attempts_container.pack(fill='x', padx=10, pady=(0, 10))
        
        # Son tahminleri en üstte göster
        for i, (guess, feedback) in enumerate(reversed(attempts)):
            attempt_num = len(attempts) - i
            
            # Her tahmin için container
            attempt_frame = tk.Frame(attempts_container, bg=self.colors['bg_light'], relief='flat', bd=1)
            attempt_frame.pack(fill='x', padx=5, pady=2)
            
            # İç frame
            inner_frame = tk.Frame(attempt_frame, bg=self.colors['bg_light'])
            inner_frame.pack(fill='x', padx=15, pady=10)
            
            # Sol taraf - tahmin numarası ve sayı
            left_frame = tk.Frame(inner_frame, bg=self.colors['bg_light'])
            left_frame.pack(side='left', fill='x', expand=True)
            
            # Tahmin numarası ve sayısı
            num_label = tk.Label(left_frame, text=f"#{attempt_num}", 
                                font=('Roboto', 10, 'bold'),
                                bg=self.colors['bg_light'], 
                                fg=self.colors['info'])
            num_label.pack(side='left')
            
            guess_label = tk.Label(left_frame, text=guess, 
                                  font=('Consolas', 18, 'bold'),
                                  bg=self.colors['bg_light'], 
                                  fg=self.colors['white'])
            guess_label.pack(side='left', padx=(10, 0))
            
            # Geri bildirim
            feedback_str = self.format_feedback(feedback)
            feedback_label = tk.Label(inner_frame, text=feedback_str, 
                                     font=('Roboto', 12, 'bold'),
                                     bg=self.colors['bg_light'], 
                                     fg=color)
            feedback_label.pack(side='right')
            
            # Kazanma durumu
            if sum(feedback) == 4:
                attempt_frame.configure(bg=self.colors['success'])
                inner_frame.configure(bg=self.colors['success'])
                left_frame.configure(bg=self.colors['success'])
                for widget in [num_label, guess_label, feedback_label]:
                    widget.configure(bg=self.colors['success'])
    
    def show_game_end_popup(self, message):
        """Oyun sonu popup'ı"""
        # Tahmin giriş alanını devre dışı bırak
        if hasattr(self, 'guess_entry') and self.guess_entry:
            self.guess_entry.config(state='disabled')
        if hasattr(self, 'guess_button') and self.guess_button:
            self.guess_button.config(state='disabled')
            
        # Bilgisayar tahmini butonunu devre dışı bırak (vs_computer modunda)
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                self._disable_guess_buttons(widget)
        
        # Oyun sonu penceresi oluştur
        end_window = tk.Toplevel(self.window)
        end_window.title("🎮 Oyun Bitti")
        end_window.geometry("500x480")
        end_window.configure(bg=self.colors['bg_dark'])
        end_window.resizable(False, False)
        
        # Pencereyi ortala
        end_window.transient(self.window)
        end_window.grab_set()
        end_window.focus_set()  # Pencereye odaklan
        
        # Ana container
        main_frame = tk.Frame(end_window, bg=self.colors['bg_dark'])
        main_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Emoji ve başlık - Kazanma/Kaybetme durumuna göre
        if "Kazandı" in message or "TEBRİKLER" in message:
            emoji = "🎉"
            title_color = self.colors['success']
            title_text = "TEBRİKLER"
        elif "Berabere" in message:
            emoji = "🤝"
            title_color = self.colors['warning']
            title_text = "BERABERE"
        else:
            emoji = "😢"
            title_color = self.colors['accent']
            title_text = "OYUN BİTTİ"
        
        # Emoji
        tk.Label(main_frame, text=emoji, font=('Arial', 72),
                bg=self.colors['bg_dark']).pack(pady=(20, 5))
        
        # Başlık
        tk.Label(main_frame, text=title_text, font=('Roboto', 24, 'bold'),
                bg=self.colors['bg_dark'], fg=title_color).pack(pady=(0, 15))
        
        # Mesaj
        msg_label = tk.Label(main_frame, text=message, font=('Roboto', 16),
                bg=self.colors['bg_dark'], fg=self.colors['text_light'],
                justify='center', wraplength=440)
        msg_label.pack(pady=(0, 20))
        
        # Butonlar - Belirgin ve büyük
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        button_frame.pack(pady=20, fill='x')
        
        # Yeni Oyun butonu - Daha belirgin
        font_settings = ('Roboto', 14, 'bold')
        restart_btn = tk.Button(
            button_frame, 
            text="🔄 YENİ OYUN", 
            command=lambda: [end_window.destroy(), self.restart_game()],
            font=font_settings,
            bg=self.colors['success'],
            fg=self.colors['white'],
            relief='flat', 
            borderwidth=0,
            padx=30, 
            pady=15,
            cursor='hand2',
            width=15
        )
        restart_btn.pack(side='left', padx=10, expand=True, fill='x')
        
        # Ana Menü butonu - Daha belirgin
        menu_btn = tk.Button(
            button_frame, 
            text="🏠 ANA MENÜ", 
            command=lambda: [end_window.destroy(), self.create_main_menu()],
            font=font_settings,
            bg=self.colors['info'],
            fg=self.colors['white'],
            relief='flat', 
            borderwidth=0,
            padx=30, 
            pady=15,
            cursor='hand2',
            width=15
        )
        menu_btn.pack(side='right', padx=10, expand=True, fill='x')
    
    def _disable_guess_buttons(self, frame):
        """Tüm tahmin butonlarını devre dışı bırakır"""
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Button) and ("TAHMİN" in widget["text"] or "Bilgisayar" in widget["text"]):
                widget.config(state='disabled')
            elif isinstance(widget, tk.Frame):
                self._disable_guess_buttons(widget)
    
    def restart_game(self):
        """Aynı modda yeni oyun başlatır"""
        if self.game_mode == "single":
            self.start_single_player()
        elif self.game_mode == "two_player":
            self.start_two_player()
        elif self.game_mode == "vs_computer":
            self.start_vs_computer()
    
    def game_won(self):
        """Oyun kazanıldığında"""
        # Yeni yaklaşım: belirlenmiş ses kanalı kullanarak win.mp3 sesi çal
        try:
            # Doğrudan sound_effects sözlüğünden al ve çal
            if self.sound_effects.get("win"):
                # Önceki tüm sesleri durdur
                pygame.mixer.stop()
                
                # Kazanma sesini ayarla ve çal
                win_sound = self.sound_effects["win"]
                win_sound.set_volume(1.0)  # Tam ses seviyesi
                
                # Belirli kanalda çal
                channel = pygame.mixer.Channel(0)  # İlk kanalı kullan
                channel.set_volume(1.0)  # Tam ses
                channel.play(win_sound)
                
                print("Kazanma sesi çalınıyor!")
            else:
                # Dosya doğrudan yüklenebiliyorsa son çare olarak dene
                sound_path = os.path.join("sounds", "win.mp3")
                if os.path.exists(sound_path):
                    win_sound = pygame.mixer.Sound(sound_path)
                    win_sound.set_volume(1.0)
                    pygame.mixer.Channel(0).play(win_sound)
                    print("Kazanma sesi alternatif yöntemle çalındı!")
                else:
                    print("HATA: Kazanma sesi bulunamadı!")
        except Exception as e:
            print(f"Kazanma sesi çalınırken kritik hata: {e}")
            
        # Kazanma mesajını hazırla
        if self.game_mode == "single":
            attempts = len(self.player1_attempts)
            message = f"🎉 TEBRİKLER! 🏆\n\nKazandınız!\n\nGizli Sayı: {self.secret_number}\n{attempts} tahminde buldunuz!"
        elif self.game_mode == "two_player":
            winner = self.current_player
            attempts = len(self.player1_attempts) if winner == 1 else len(self.player2_attempts)
            message = f"🎉 TEBRİKLER! 🏆\n\nOyuncu {winner} Kazandı!\n\nGizli Sayı: {self.secret_number}\n{attempts} tahminde buldu!"
        elif self.game_mode == "vs_computer":
            attempts = len(self.player1_attempts)
            message = f"🎉 TEBRİKLER! 🏆\n\nKazandınız!\n\nGizli Sayı: {self.secret_number}\n{attempts} tahminde buldunuz!"
        
        self.show_game_end_popup(message)
    
    def game_lost(self):
        """Oyun kaybedildiğinde"""
        # Yeni yaklaşım: belirlenmiş ses kanalı kullanarak lose.mp3 sesi çal
        try:
            # Doğrudan sound_effects sözlüğünden al ve çal
            if self.sound_effects.get("lose"):
                # Önceki tüm sesleri durdur
                pygame.mixer.stop()
                
                # Kaybetme sesini ayarla ve çal
                lose_sound = self.sound_effects["lose"]
                lose_sound.set_volume(1.0)  # Tam ses seviyesi
                
                # Belirli kanalda çal
                channel = pygame.mixer.Channel(1)  # İkinci kanalı kullan
                channel.set_volume(1.0)  # Tam ses
                channel.play(lose_sound)
                
                print("Kaybetme sesi çalınıyor!")
            else:
                # Dosya doğrudan yüklenebiliyorsa son çare olarak dene
                sound_path = os.path.join("sounds", "lose.mp3")
                if os.path.exists(sound_path):
                    lose_sound = pygame.mixer.Sound(sound_path)
                    lose_sound.set_volume(1.0)
                    pygame.mixer.Channel(1).play(lose_sound)
                    print("Kaybetme sesi alternatif yöntemle çalındı!")
                else:
                    print("HATA: Kaybetme sesi bulunamadı!")
        except Exception as e:
            print(f"Kaybetme sesi çalınırken kritik hata: {e}")
            
        message = f"😢 OYUN BİTTİ\n\nHakkınız bitti!\n\nGizli Sayı: {self.secret_number}\n\nUmarım bir dahaki sefere daha şanslı olursunuz!"
        self.show_game_end_popup(message)
    
    def run(self):
        """Oyunu başlatır"""
        # Pencere ikonunu ayarla (opsiyonel)
        try:
            self.window.iconbitmap('game_icon.ico')
        except:
            pass
        
        # Pencere kapanma olayını yakala
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Ana döngüyü başlat
        self.window.mainloop()
    
    def on_closing(self):
        """Pencere kapanırken çalışır"""
        if messagebox.askokcancel("Çıkış", "Oyundan çıkmak istediğinizden emin misiniz?"):
            self.window.destroy()

    def adjust_color(self, color: str, amount: int) -> str:
        """Rengin parlaklığını ayarlar"""
        # Renk kodunu RGB bileşenlerine ayır
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Her bileşeni ayarla
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Yeni renk kodunu döndür
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def load_sound(self, filename):
        """Ses dosyasını yükler"""
        try:
            sound_path = os.path.join("sounds", filename)
            # Ses dosyası yoksa None döndür
            if not os.path.exists(sound_path):
                print(f"Ses dosyası bulunamadı: {sound_path}")
                return None
            
            # Mixer'ın başlatıldığından emin ol
            if not pygame.mixer.get_init():
                print("Mixer başlatılmamış, başlatılıyor...")
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            
            # Ses dosyasını yükle
            sound = pygame.mixer.Sound(sound_path)
            
            # Ses dosyasını test et
            sound.set_volume(0.0)  # Sessiz test
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound, maxtime=100)  # Kısa bir süre çal ve durdur
                channel.stop()
            
            # Normal ses seviyesine geri getir
            sound.set_volume(0.5)
            
            print(f"Ses dosyası başarıyla yüklendi: {filename}")
            return sound
        except Exception as e:
            print(f"Ses dosyası yüklenirken hata: {filename} - {e}")
            return None

    def play_sound(self, sound_name):
        """Belirlenen sesi çalar"""
        # Ses kapalıysa ve win/lose seslerinden biri değilse çalma
        if not self.is_sound_on and sound_name not in ["win", "lose"]:
            return False
        
        try:
            # Ses efekti kontrolü
            if sound_name in self.sound_effects and self.sound_effects[sound_name]:
                sound = self.sound_effects[sound_name]
                
                # Win ve lose seslerini özel kanallar üzerinden çal
                if sound_name == "win":
                    # Önceki sesleri durdur
                    pygame.mixer.stop()
                    # Kazanma sesini yüksek sesle çal
                    sound.set_volume(1.0)
                    channel = pygame.mixer.Channel(0)
                    channel.set_volume(1.0)
                    channel.play(sound)
                    print(f"{sound_name} sesi özel kanal 0'da çalınıyor")
                elif sound_name == "lose":
                    # Önceki sesleri durdur
                    pygame.mixer.stop()
                    # Kaybetme sesini yüksek sesle çal
                    sound.set_volume(1.0)
                    channel = pygame.mixer.Channel(1)
                    channel.set_volume(1.0)
                    channel.play(sound)
                    print(f"{sound_name} sesi özel kanal 1'de çalınıyor")
                else:
                    # Diğer sesleri normal ses seviyesiyle çal
                    volume = 0.5
                    sound.set_volume(volume)
                    
                    # Boş bir kanal bul ve ses çal
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(sound)
                    else:
                        # Tüm kanallar dolu ise, doğrudan çal
                        sound.play()
                    
                    print(f"{sound_name} sesi çalınıyor")
                
                return True
            else:
                # Ses dosyası bulunamadıysa alternatif yöntem dene
                sound_path = os.path.join("sounds", f"{sound_name}.mp3")
                if os.path.exists(sound_path):
                    try:
                        # Ses dosyasını doğrudan yükle ve çal
                        temp_sound = pygame.mixer.Sound(sound_path)
                        volume = 1.0 if sound_name in ["win", "lose"] else 0.5
                        temp_sound.set_volume(volume)
                        
                        # Özel kanal kullan
                        channel_num = 0 if sound_name == "win" else (1 if sound_name == "lose" else 2)
                        pygame.mixer.Channel(channel_num).play(temp_sound)
                        print(f"{sound_name} sesi alternatif yöntemle çalındı")
                        return True
                    except Exception as e:
                        print(f"Alternatif ses çalma hatası: {e}")
                        return False
                
                print(f"{sound_name} sesi için dosya bulunamadı")
                return False
        except Exception as e:
            print(f"Ses çalma hatası ({sound_name}): {e}")
            return False
    
    def play_background_music(self):
        """Arka plan müziğini çalar"""
        if self.is_music_on:
            try:
                # Müziği yükle
                sound_path = os.path.join("sounds", "background_music.mp3")
                if os.path.exists(sound_path):
                    # Müzik modülünü sıfırla
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    
                    # Yeni müziği yükle ve çal
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.set_volume(0.3)  # Müzik sesini %30 olarak ayarla
                    pygame.mixer.music.play(-1)  # -1 sonsuz döngüde çalması için
                    
                    print("Arka plan müziği başlatıldı")
                else:
                    print(f"Müzik dosyası bulunamadı: {sound_path}")
            except Exception as e:
                print(f"Müzik yüklenirken hata: {e}")
                self.is_music_on = False
    
    def toggle_music(self):
        """Müziği açıp kapatır"""
        self.is_music_on = not self.is_music_on
        if self.is_music_on:
            self.play_background_music()
        else:
            pygame.mixer.music.stop()
        
        # Butonu anında güncelle
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                self._update_music_button_in_frame(widget)
        
        # Ses efekti
        self.play_sound("button_click")
    
    def _update_music_button_in_frame(self, frame):
        """Frameler içinde müzik butonunu bulup günceller"""
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Button) and (("🎵" in widget["text"] and "🚫" not in widget["text"]) or 
                                                ("🎵🚫" in widget["text"])):
                music_icon = "🎵" if self.is_music_on else "🎵🚫"
                widget.config(text=music_icon)
            elif isinstance(widget, tk.Frame):
                self._update_music_button_in_frame(widget)
    
    def toggle_sound(self):
        """Ses efektlerini açıp kapatır"""
        self.is_sound_on = not self.is_sound_on
        
        # Butonu anında güncelle
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                self._update_sound_button_in_frame(widget)
        
        # Ses efekti (eğer açık ise)
        if self.is_sound_on:
            self.play_sound("button_click")
    
    def _update_sound_button_in_frame(self, frame):
        """Frameler içinde ses butonunu bulup günceller"""
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Button) and ("🔊" in widget["text"] or "🔇" in widget["text"]):
                sound_icon = "🔊" if self.is_sound_on else "🔇"
                widget.config(text=sound_icon)
            elif isinstance(widget, tk.Frame):
                self._update_sound_button_in_frame(widget)

    def create_user_vs_cpu_interface(self):
        """Kullanıcı vs Bilgisayar modu arayüzünü oluşturur"""
        # Pencereyi temizle
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Mevcut arayüzü user_vs_cpu_interface olarak ayarla
        self.current_interface = "user_vs_cpu_interface"
        
        # Ana container
        main_container = tk.Frame(self.window, bg=self.colors['bg_dark'])
        main_container.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Üst başlık
        header_frame = tk.Frame(main_container, bg=self.colors['bg_medium'], height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Başlık container
        title_container = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        title_container.pack(expand=True, fill='both', padx=20)
        
        # Tema ve ses butonları
        # Tema değiştirme butonu
        theme_icon = "🌞" if self.is_dark_mode else "🌙"
        theme_button = tk.Button(
            title_container,
            text=theme_icon,
            command=self.toggle_theme,
            font=('Roboto', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        theme_button.pack(side='right', padx=5, pady=5)
        
        # Müzik açma/kapama butonu
        music_icon = "🎵" if self.is_music_on else "🎵🚫"
        music_button = tk.Button(
            title_container,
            text=music_icon,
            command=self.toggle_music,
            font=('Roboto', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        music_button.pack(side='right', padx=5, pady=5)
        

        
        # Oyun modu başlığı
        title_text = "🎲 Kullanıcı vs Bilgisayar"
        title_label = tk.Label(
            title_container, 
            text=title_text,
            font=('Roboto', 20, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent']
        )
        title_label.pack(side='left', expand=True)
        
        # Ana içerik container
        content_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content_frame.pack(expand=True, fill='both')
        
        # Bilgisayarın sayısı bilgi etiketi
        info_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'], padx=20, pady=15)
        info_frame.pack(fill='x', pady=10)
        
        cpu_secret_label = tk.Label(
            info_frame,
            text=f"Bilgisayarın gizli sayısı: {self.cpu_guess_number if self.cpu_guess_number else '????'}",
            font=('Roboto', 16, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['warning']
        )
        cpu_secret_label.pack(side='left')
        
        # Kullanıcı tahmin kısmı
        user_frame = tk.Frame(content_frame, bg=self.colors['bg_light'])
        user_frame.pack(fill='x', pady=10)
        
        tk.Label(
            user_frame,
            text="👤 SİZİN TAHMİNİNİZ",
            font=('Roboto', 14, 'bold'),
            bg=self.colors['bg_light'],
            fg=self.colors['info']
        ).pack(pady=10)
        
        # Tahmin input container
        user_input_frame = tk.Frame(user_frame, bg=self.colors['bg_light'])
        user_input_frame.pack(pady=10)
        
        self.user_guess_entry = tk.Entry(
            user_input_frame,
            font=('Roboto', 16, 'bold'),
            width=8,
            justify='center',
            bg=self.colors['bg_medium'],
            fg=self.colors['white'],
            relief='flat',
            bd=5
        )
        self.user_guess_entry.pack(side='left', padx=10)
        
        self.user_guess_button = self.create_rounded_button(
            user_input_frame,
            "🎮 TAHMİN ET",
            self.user_make_guess,
            self.colors['info'],
            font=('Roboto', 14, 'bold')
        )
        self.user_guess_button.pack(side='left', padx=10)
        
        # Kalan hak bilgisi
        user_attempts_left = self.max_attempts - len(self.player1_attempts)
        self.user_attempts_label = tk.Label(
            user_frame,
            text=f"Kalan hakkınız: {user_attempts_left}",
            font=('Roboto', 12),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light']
        )
        self.user_attempts_label.pack(pady=5)
        
        # Bilgisayar tahmin kısmı
        cpu_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        cpu_frame.pack(fill='x', pady=10)
        
        tk.Label(
            cpu_frame,
            text="🤖 BİLGİSAYAR TAHMİNİ",
            font=('Roboto', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['warning']
        ).pack(pady=10)
        
        # Bilgisayar tahmin butonu
        cpu_input_frame = tk.Frame(cpu_frame, bg=self.colors['bg_medium'])
        cpu_input_frame.pack(pady=10)
        
        # Bilgisayar tahmin giriş alanı - düzenleme için
        self.cpu_guess_entry = tk.Entry(
            cpu_input_frame,
            font=('Roboto', 16, 'bold'),
            width=8,
            justify='center',
            bg=self.colors['bg_light'],
            fg=self.colors['warning'],
            relief='flat',
            bd=5
        )
        self.cpu_guess_entry.pack(side='left', padx=10)
        
        # Seçenekler - bilgisayar tahmini için geri bildirim
        feedback_frame = tk.Frame(cpu_input_frame, bg=self.colors['bg_medium'])
        feedback_frame.pack(side='left', padx=10)
        
        feedback_options = [
            ("✅ +1", 1),
            ("⚠️ -1", -1),
            ("❌ 0", 0)
        ]
        
        # Geri bildirim seçenekleri
        self.feedback_vars = []
        for i in range(4):  # 4 basamak için 4 değişken
            var = tk.IntVar(value=0)
            self.feedback_vars.append(var)
            
            position_frame = tk.Frame(feedback_frame, bg=self.colors['bg_medium'])
            position_frame.pack(side='left', padx=5)
            
            # Basamak numarası
            tk.Label(
                position_frame,
                text=f"{i+1}.",
                font=('Roboto', 12, 'bold'),
                bg=self.colors['bg_medium'],
                fg=self.colors['white']
            ).pack()
            
            # Her basamak için geri bildirim seçenekleri
            for text, value in feedback_options:
                rb = tk.Radiobutton(
                    position_frame,
                    text=text,
                    variable=var,
                    value=value,
                    bg=self.colors['bg_medium'],
                    fg=self.colors['text_light'],
                    selectcolor=self.colors['bg_dark'],
                    font=('Roboto', 10),
                    relief='flat',
                    borderwidth=0
                )
                rb.pack(anchor='w')
        
        # Bilgisayar tahmin gönderme butonu
        self.cpu_guess_button = self.create_rounded_button(
            cpu_frame,
            "🎯 BİLGİSAYAR TAHMİNİ GÖNDER",
            self.computer_make_guess,
            self.colors['warning'],
            font=('Roboto', 14, 'bold')
        )
        self.cpu_guess_button.pack(pady=10)
        
        # Bilgisayar kalan hak bilgisi
        cpu_attempts_left = self.max_attempts - len(self.computer_attempts)
        self.cpu_attempts_label = tk.Label(
            cpu_frame,
            text=f"Bilgisayar kalan hakkı: {cpu_attempts_left}",
            font=('Roboto', 12),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_light']
        )
        self.cpu_attempts_label.pack(pady=5)
        
        # Tahmin geçmişi
        history_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        history_frame.pack(fill='both', expand=True, pady=10)
        
        # Geçmiş etiketleri
        tk.Label(
            history_frame,
            text="📜 TAHMİN GEÇMİŞİ",
            font=('Roboto', 16, 'bold'),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_light']
        ).pack(pady=10)
        
        # Scrollable tahmin geçmişi
        history_container = tk.Frame(history_frame, bg=self.colors['bg_medium'])
        history_container.pack(fill='both', expand=True, padx=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(history_container, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(history_container, orient="vertical", command=canvas.yview)
        self.history_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        self.history_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Fare tekerleği ile kaydırma
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Ana menü dönüş butonu
        back_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        back_frame.pack(fill='x', pady=10)
        
        back_button = self.create_rounded_button(
            back_frame,
            "🏠 ANA MENÜYE DÖN",
            self.create_main_menu,
            self.colors['accent'],
            font=('Roboto', 12, 'bold')
        )
        back_button.pack(pady=5)
        
        # Enter tuşu ile tahmin
        self.user_guess_entry.bind('<Return>', lambda e: self.user_make_guess())
        self.user_guess_entry.focus()
        
        # İlk bilgisayar tahmini
        if not self.computer_attempts:
            self.generate_computer_guess()
    
    def user_make_guess(self):
        """Kullanıcının tahmin yapması"""
        if self.game_mode != "user_vs_cpu":
            return
            
        guess = self.user_guess_entry.get().strip()
        
        # Tahmin geçerliliğini kontrol et
        is_valid, error_msg = self.validate_guess(guess)
        if not is_valid:
            self.show_error_popup(error_msg)
            return
        
        # Geri bildirim hesapla
        feedback = self.calculate_feedback(self.cpu_guess_number, guess)
        
        # Tahmin geçmişine ekle
        self.player1_attempts.append((guess, feedback))
        
        # Ses efekti
        if sum(feedback) == 4:
            self.play_sound("win")
        elif sum(feedback) > 0:
            self.play_sound("correct")
        else:
            self.play_sound("wrong")
        
        # Giriş alanını temizle
        self.user_guess_entry.delete(0, 'end')
        
        # Kazanma kontrolü
        if sum(feedback) == 4:
            self.show_game_end_popup(
                f"🎉 TEBRİKLER! 🏆\n\nKazandınız!\n\nBilgisayarın Gizli Sayısı: {self.cpu_guess_number}\n"
                f"{len(self.player1_attempts)} tahminde buldunuz!"
            )
            return
        
        # Hak kontrolü
        if len(self.player1_attempts) >= self.max_attempts:
            self.show_game_end_popup(
                f"😢 OYUN BİTTİ\n\nHakkınız bitti!\n\n"
                f"Bilgisayarın Gizli Sayısı: {self.cpu_guess_number}"
            )
            return
        
        # Kullanıcı kalan hakları güncelle
        user_attempts_left = self.max_attempts - len(self.player1_attempts)
        self.user_attempts_label.config(text=f"Kalan hakkınız: {user_attempts_left}")
        
        # Tahmin geçmişini güncelle
        self.update_user_vs_cpu_history()
    
    def generate_computer_guess(self):
        """Bilgisayar tahmini oluştur ve UI'a yerleştir"""
        # Bilgisayar tahmini
        computer_guess = self.computer_make_guess()
        
        # Tahmin alanını doldur
        self.cpu_guess_entry.delete(0, 'end')
        self.cpu_guess_entry.insert(0, computer_guess)
    
    def update_user_vs_cpu_history(self):
        """Kullanıcı vs Bilgisayar modu için tahmin geçmişini günceller"""
        # Geçmiş frame'i temizle
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        # Kullanıcı tahminleri
        self.display_player_history(
            "👤 SİZİN TAHMİNLERİNİZ", 
            self.player1_attempts, 
            self.colors['info']
        )
        
        # Bilgisayar tahminleri
        if self.computer_attempts:
            tk.Frame(self.history_frame, bg=self.colors['bg_medium'], height=20).pack()
            self.display_player_history(
                "🤖 BİLGİSAYAR TAHMİNLERİ", 
                self.computer_attempts, 
                self.colors['warning']
            )

    def computer_guess(self):
        """Bilgisayar tahmin yapar"""
        if self.game_mode != "vs_computer":
            return
        
        # Düşünme animasyonu - daha kısa süre
        self.show_thinking_animation()
        
        # Gerçek tahmin kısa bir gecikme ile
        self.window.after(800, self.execute_computer_guess)    

    def show_thinking_animation(self):
        """Bilgisayar düşünme animasyonu"""
        thinking_window = tk.Toplevel(self.window)
        thinking_window.title("🤖 Bilgisayara Düşünüyor...")
        thinking_window.geometry("300x150")
        thinking_window.configure(bg=self.colors['bg_dark'])
        thinking_window.resizable(False, False)
        
        # Pencereyi ortala
        thinking_window.transient(self.window)
        thinking_window.grab_set()
        
        tk.Label(thinking_window, text="🤖", font=('Arial', 48),
                bg=self.colors['bg_dark'], fg=self.colors['warning']).pack(pady=20)
        
        thinking_label = tk.Label(thinking_window, text="Düşünüyorum", 
                                 font=('Roboto', 14),
                                 bg=self.colors['bg_dark'], 
                                 fg=self.colors['text_light'])
        thinking_label.pack()
        
        # Nokta animasyonu
        def animate_dots(count=0):
            dots = "." * ((count % 4) + 1)
            thinking_label.configure(text=f"Düşünüyorum{dots}")
            if thinking_window.winfo_exists():
                thinking_window.after(200, lambda: animate_dots(count + 1))
        
        animate_dots()
        
        # 0.8 saniye sonra kapat
        self.window.after(800, thinking_window.destroy)

def check_pygame_mixer():
    """Pygame mixer durumunu kontrol eder ve raporlar"""
    print("\n--- Pygame Ses Sistemi Kontrolü ---")
    
    try:
        if not pygame.mixer.get_init():
            print("HATA: Pygame mixer başlatılmamış!")
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            print("Pygame mixer yeniden başlatıldı.")
        
        # Sadece mixer hazır mı kontrolü yap
        if pygame.mixer.get_init():
            print("Pygame mixer HAZIR")
            
            channels = pygame.mixer.get_num_channels()
            print(f"Kullanılabilir Ses Kanalı Sayısı: {channels}")
            
            if pygame.mixer.music.get_busy():
                print("Arka plan müziği ÇALIYOR")
            else:
                print("Arka plan müziği ÇALMIYOR")
        else:
            print("Pygame mixer HAZIR DEĞİL!")
        
        print("--- Mixer Kontrolü Tamamlandı ---\n")
        return True
    except Exception as e:
        print(f"Pygame mixer kontrol edilirken hata: {e}")
        return False
        
if __name__ == "__main__":
    # Pygame başlat
    pygame.init()
    
    # Mixer durumunu kontrol et
    check_pygame_mixer()
    
    # Oyunu başlat
    game = PPGGame()
    game.run()