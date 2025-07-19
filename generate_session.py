import instaloader
import base64

def generate_session():
    """Lokal kompyuterda Instagram sessiya faylini yaratadi va uni kodlaydi."""
    L = instaloader.Instaloader()
    try:
        username = input("Instagram foydalanuvchi nomingizni kiriting: ")
        password = input("Instagram parolingizni kiriting: ")
        
        print(f"'{username}' sifatida Instagramga kirilmoqda...")
        L.login(username, password)
        
        # Sessiya faylini saqlash
        session_filename = f"{username}"
        L.save_session_to_file(session_filename)
        
        print(f"\nMuvaffaqiyatli! '{session_filename}' nomli sessiya fayli yaratildi.")

        # Faylni o'qish va base64 formatida kodlash
        with open(session_filename, 'rb') as f:
            encoded_session = base64.b64encode(f.read()).decode('utf-8')
        
        print("\n--- BU YERDAN NUSXA OLING ---")
        print("Quyidagi kodlangan matnni to'liq nusxalab oling va Railway'dagi INSTA_SESSION_BASE64 o'zgaruvchisiga joylashtiring:")
        print("\n" + encoded_session)
        print("\n--- NUSXA OLISHNI TUGATING ---")

    except Exception as e:
        print(f"\nXatolik yuz berdi: {e}")

if __name__ == "__main__":
    generate_session()
