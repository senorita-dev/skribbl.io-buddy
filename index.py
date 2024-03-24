import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import WebDriver


def run(invite_link):
    with webdriver.Firefox() as driver:
        join_game(driver, invite_link)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#game-word .description.waiting")
            )
        )
        print("Joined Game, waiting for host to start game...")
        input("Started game?")
        game_state = get_game_state(driver)
        match game_state:
            case "Choose a word":
                # Buddy is choosing a word
                pass
            case _:
                # Buddy is drawing
                pass
        
        input('end')
        pass
    pass


def join_game(driver: WebDriver, invite_link: str):
    driver.get(invite_link)
    assert driver.title == "skribbl - Free Multiplayer Drawing & Guessing Game"
    elem_name = driver.find_element(By.CLASS_NAME, "input-name")
    elem_name.send_keys("skribblio-bot")
    elem_play = driver.find_element(By.CLASS_NAME, "button-play")
    elem_play.click()
    pass


def wait_for_game_start(driver: WebDriver):
    WebDriverWait(driver, 30).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, "#game-word .description.waiting"))
	)
    pass


def get_game_state(driver: WebDriver) -> str:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".text.show")))
    elem_state = driver.find_element(By.CSS_SELECTOR, ".text.show")
    return elem_state.text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python index.py <invite link>")
        sys.exit(1)
    invite_link = sys.argv[1]
    run(invite_link)
    pass
