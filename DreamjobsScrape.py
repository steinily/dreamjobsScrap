# %%
from selenium import webdriver
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# %% [markdown]
# #Variables

# %%
url = 'https://dreamjo.bs/hu/jobs'

databasename = str(pd.to_datetime("today").date()) + ' dreamjo_bs.db'
engine = create_engine('sqlite:///' + databasename, echo=False)

job_description = {
    'Indicator': [],
    'Company': [],
    'Position': [],
    'PositionInfo': [],
    'Type': [],
    'SalaryInfo': [],
    'Salary': [],
    'Link': []
}

# %% [markdown]
# # Chrome Driver setup

# %%
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)  # options=chrome_options
driver.get(url)

# %%


def getjobsection():
    elements = driver.find_elements(By.CLASS_NAME, 'page-section')
    for i in range(len(elements)):
        if elements[i].get_attribute('class') == 'page-section':
            jobsection = elements[i]
    return jobsection

# %%


def dictappend():
    jobpage = getjobsection()
    company = jobpage.find_elements(
        By.CLASS_NAME, 'job-card-ultimate__company-name')
    position = jobpage.find_elements(
        By.CLASS_NAME, 'job-card-ultimate__job-name')
    positionInfo = jobpage.find_elements(
        By.CLASS_NAME, 'job-card-ultimate__tags ')
    type = jobpage.find_elements(
        By.CLASS_NAME, 'job-card-ultimate__header-category-tag')
    salaryInfo = jobpage.find_elements(By.CLASS_NAME, 'salary-label__type')
    salary = jobpage.find_elements(By.CLASS_NAME, 'salary-label__salary ')
    link = jobpage.find_elements(By.CLASS_NAME, 'job-card-ultimate__job-name')
    for i in range(len(company)):
        indexincrement = len(job_description['Indicator'])
        job_description['Indicator'].append(indexincrement)
        job_description['Company'].append(company[i].text)
        job_description['Position'].append(position[i].text)
        job_description['PositionInfo'].append(
            positionInfo[i].text.replace('\n', ' '))
        job_description['Type'].append(type[i].text)
        job_description['SalaryInfo'].append(salaryInfo[i].text)
        job_description['Salary'].append(salary[i].text)
        job_description['Link'].append(link[i].get_attribute('href'))


# %% [markdown]
# # Paging

# %%
page = 1
while True:
    url = "https://dreamjo.bs/hu/jobs?page="+str(page)
    driver.get(url)
    if len(driver.find_elements(By.CLASS_NAME, 'error-code')) == 1:
        break
    dictappend()
    page += 1
    print(f"Current page : {url}")
    print(f"Jobs count : {len(job_description['Indicator'])}")


# %% [markdown]
# # Scraped data to XLSX and Db

# %%
df = pd.DataFrame(job_description)
df = df.drop('Indicator', axis=1)
df.to_excel(str(pd.to_datetime("today").date()) + ' dreamjo_bs.xlsx')
df.to_sql('job_description', con=engine, if_exists='append')
driver.quit()
