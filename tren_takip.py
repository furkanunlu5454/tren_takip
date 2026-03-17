import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- AYARLAR ---
TOKEN = "8751432623:AAFPIUJwTbmN_4f6PJjIus71THyL9kDbgTU"
CHAT_ID = "1493943101"
HEDEF_SAATLER = ["15:10", "15:40", "17:25", "18:20", "18:55"]

def bildirim_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mesaj}"
    try: requests.get(url)
    except: pass

def bilet_sorgula():
    options = webdriver.ChromeOptions()
    # --- GİZLİ AJAN MODU AYARLARI ---
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Bot olduğumuzu gizleyen JavaScript komutu
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    wait = WebDriverWait(driver, 25)

    try:
        print(f"[{time.strftime('%H:%M:%S')}] Siteye giriş denemesi...")
        driver.get("https://ebilet.tcddtasimacilik.gov.tr/view/eybis/tnmGenel/tcdd_islem.jsf")
        time.sleep(5)

        # NEREDEN - Daha yavaş ve insancıl yazma
        nereden = wait.until(EC.element_to_be_clickable((By.ID, "nereden")))
        nereden.click()
        for char in "İstanbul(Söğütlüçeşme)":
            nereden.send_keys(char)
            time.sleep(0.1) # Harf harf yazıyormuş gibi
        time.sleep(1)
        nereden.send_keys(Keys.ENTER)

        # NEREYE
        nereye = driver.find_element(By.ID, "nereye")
        for char in "Bilecik":
            nereye.send_keys(char)
            time.sleep(0.1)
        time.sleep(1)
        nereye.send_keys(Keys.ENTER)

        # TARİH
        tarih = driver.find_element(By.ID, "trCalGid_input")
        tarih.click()
        tarih.send_keys(Keys.CONTROL + "a")
        tarih.send_keys(Keys.BACKSPACE)
        tarih.send_keys("18.03.2026")
        tarih.send_keys(Keys.ENTER)
        time.sleep(2)

        # SORGULA
        driver.find_element(By.ID, "btnSeferSorgula").click()
        print("Sorgulandı, veriler bekleniyor...")
        time.sleep(10)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        found = False
        if "Seç" in body_text:
            for saat in HEDEF_SAATLER:
                if saat in body_text:
                    bildirim_gonder(f"Furki! {saat} trenini kontrol et, yer açılmış olabilir!")
                    found = True
        
        if not found:
            print("Kontrol edildi: Boş yer yok.")

    except Exception as e:
        print(f"Hata: {e}")
    finally:
        driver.quit()

print("Bilet avcısı (Gizli Mod) devrede...")
while True:
    bilet_sorgula()
    time.sleep(180)
