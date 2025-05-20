# I use here patchright -- patched and undetected version of the Playwright Testing and Automation Framework.
from patchright.sync_api import sync_playwright, Playwright
import json, time
from database import create_table_if_not_exists, insert_item_if_not_exists, insert_item

# Тут збираються дані про всі товари на сторінках і все працює стабільно
def scrap_atb(playwright: Playwright, choice):
    urls = {
        # Аналіз лише по цим 5
        "1": {"url": "https://www.atbmarket.com/catalog/287-ovochi-ta-frukti", "category": "Овочі та фрукти"},
        "2": {"url": "https://www.atbmarket.com/catalog/molocni-produkti-ta-ajca", "category": "Молочні продукти та яйця"},
        "3": {"url": "https://www.atbmarket.com/catalog/325-khlibobulochni-virobi", "category": "Хлібобулочні вироби"},
        "4": {"url": "https://www.atbmarket.com/catalog/294-napoi-bezalkogol-ni", "category": "Напої безалкогольні"},
        "5": {"url": "https://www.atbmarket.com/catalog/kava-caj", "category": "Кава та чай"},
        
        # Додаткові, нехай будуть
        "6": {"url": "https://www.atbmarket.com/catalog/siri", "category": "Сири"},
        "7": {"url": "https://www.atbmarket.com/catalog/maso", "category": "М'ясо"},
        "8": {"url": "https://www.atbmarket.com/catalog/299-konditers-ki-virobi", "category": "Кондитерські вироби"},
        "9": {"url": "https://www.atbmarket.com/catalog/353-riba-i-moreprodukti", "category": "Риба та морепродукти"},
        "10": {"url": "https://www.atbmarket.com/catalog/285-bakaliya", "category": "Бакалія"},
        "11": {"url": "https://www.atbmarket.com/catalog/322-zamorozheni-produkti", "category": "Заморожені продукти"},
        "12": {"url": "https://www.atbmarket.com/catalog/cipsi-sneki", "category": "Чіпси та снеки"},
        "13": {"url": "https://www.atbmarket.com/catalog/360-kovbasa-i-m-yasni-delikatesi", "category": "Ковбаси та м'ясні делікатеси"},
        "14": {"url": "https://www.atbmarket.com/catalog/339-dityache-kharchuvannya", "category": "Дитяче харчування"},
        "15": {"url": "https://www.atbmarket.com/catalog/292-alkogol-i-tyutyun", "category": "Алкоголь та тютюн"}
    }

    start_url = urls.get(choice)
    if not start_url:
        print("No such choice")
        exit()

    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url["url"])

    # Підтвердження віку тільки для сторінки алкоголю/тютюну
    if choice == "15":
        try:
            age_button = page.locator('button.alcohol-modal__submit')
            if age_button.is_visible():
                age_button.click()
                page.wait_for_timeout(500)
        except:
            pass

    while True:
        for link in page.locator('a.catalog-item__photo-link').all():
            p = browser.new_page(base_url="https://www.atbmarket.com/")
            url = link.get_attribute("href")
            if url:
                p.goto(url)
                data = p.locator('script[type="application/ld+json"]').nth(1).text_content()
                json_data = json.loads(data)
                offers = json_data["offers"]
                url = offers["url"]
                category = start_url["category"]
                
                # print("Назва товару:", json_data["name"])
                # print("Ціна:", offers["price"])
                # print("Валюта:", offers["priceCurrency"])
                # print("URL товару:", offers["url"])
                # print("------")
                
                insert_item(
                    json_data["name"],
                    float(offers["price"]),
                    offers["priceCurrency"],
                    offers["url"],
                    category
                )
                print(f"Товар {url} вставлено в таблицю")
            p.close()

        # Переходимо на наступну сторінку
        current_url = page.url
        next_button = page.locator('li.product-pagination__item.next a.product-pagination__link')

        if next_button.count() > 0:
            next_button.first.click()
            page.wait_for_load_state("networkidle")
            if page.url == current_url:
                print("Остання сторінка. Завершення.")
                break
        else:
            print("Остання сторінка. Завершення.")
            break
        

"""На сайті Сільпо в мене проблема з динамічною загрузкою -- Той самий код в мене працює "через раз".
Тому поки що, збираються дані не про всі товари, але, думаю, того що є буде достатньо"""
def scrap_silpo(playwright: Playwright, choice):
    urls = {
        "1": {"url": "https://silpo.ua/category/frukty-ovochi-4788", "category": "Овочі та фрукти"},
        "2": {"url": "https://silpo.ua/category/khlib-ta-vypichka-5121", "category": "Хлібобулочні вироби"},
        "3": {"url": "https://silpo.ua/category/molochni-produkty-ta-iaitsia-234", "category": "Молочні продукти та яйця"},
        "4": {"url": "https://silpo.ua/category/napoi-52", "category": "Напої безалкогольні"},
        "5": {"url": "https://silpo.ua/category/kava-chai-359", "category": "Кава та чай"}
    }

    start_url = urls.get(choice)
    if not start_url:
        print("No such choice")
        exit()

    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url["url"])
    time.sleep(1)
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    

    # Натискаємо "Показати ще", поки вона є (працює не завжди, доводиться натискати вручну)
    while True:
        try:
            current_count = page.locator('a.product-card').count()
            show_more = page.locator('button.pagination__more')
            if show_more.is_visible():
                show_more.click()
                # Чекаємо, поки з'явиться хоча б один новий товар
                page.wait_for_function(
                    f'document.querySelectorAll("a.product-card").length > {current_count}'
                )
                time.sleep(1)
            else:
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    # Коли всі товари підвантажені — збираємо їх
    for link in page.locator('a.product-card').all():
        p = browser.new_page(base_url="https://silpo.ua/")
        url = link.get_attribute("href")
        if url:
            p.goto(url)
            try:
                data = p.locator('script[type="application/ld+json"]').nth(2).text_content()
                json_data = json.loads(data)
                offers = json_data["offers"]
                url = offers["url"]
                category = start_url["category"]
                
                # print("Назва товару:", json_data["name"])
                # print("Ціна:", offers["price"])
                # print("Валюта:", offers["priceCurrency"])
                # print("URL товару:", offers["url"])
                # print("------")
                
                insert_item(
                    json_data["name"],
                    float(offers["price"]),
                    offers["priceCurrency"],
                    offers["url"],
                    category
                )
                print(f"Товар {url} вставлено в таблицю")
            except Exception as e:
                print(f"❌ Помилка обробки: {e}")
        p.close()

    browser.close()
                

if __name__ == "__main__":
    create_table_if_not_exists()
    print("Make a choice: ")
    choice = input()
    with sync_playwright() as playwright:
        # scrap_atb(playwright, choice)
        scrap_silpo(playwright, choice)