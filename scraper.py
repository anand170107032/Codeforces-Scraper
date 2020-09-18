"""
    created by Manish Anand
"""
import os
import requests
import re


from bs4 import BeautifulSoup

SUBMISSION_BASE_URL = "https://codeforces.com/contest/"
BASE_URL = "https://codeforces.com/submissions/"


def fetch_data(url):
    """
	Fetch HTML data from the given url
	"""
    content = requests.get(url)
    soup = BeautifulSoup(content.text, "html.parser")
    return soup


def save_local(number, name, code, lang="cpp"):
    """
	Save the date in local file
	/number/name.lang
	"""
    curr_dir = os.getcwd()
    req_dir = os.path.join(curr_dir , number)
    if not os.path.exists(req_dir):
        os.mkdir(req_dir)
    os.chdir(req_dir)

    name += '.' + lang
    req_dir = os.path.join(req_dir , name)
    if os.path.exists(req_dir):
        os.chdir(curr_dir)
        return

    name = name.replace('/' , '')
    name = name.replace('\\' , '')
    name = name.replace('?' , '')
    name = name.replace(':' , '')
    name = name.replace('*' , '')
    name = name.replace('\"' , '')
    name = name.replace('<' , '')
    name = name.replace('>' , '')
    name = name.replace('|' , '')

    file = open(name , 'w')
    cnt = 0
    lines = code[0].split('\n')
    for line in lines:
        file.write(line)
    file.close()
    
    os.chdir(curr_dir)


def fetch_accepted_code(row, list_of_ids, file):
    """
	Fetch the accepted solutions
	"""
    id_cell = row.find('td' , {'class' : 'id-cell'})
    id = id_cell.get_text().strip()
    for p_id in list_of_ids:
        if(p_id.strip('\n') == id):
            return  
    td_cols = row.find_all('td' , {'class' : 'status-small'})

    problem_name = None
    for td in td_cols:
        anchorTag = td.find('a')
        if anchorTag is not None:
            problem_type = anchorTag['href'].split('/')[1]
            problem_no = anchorTag['href'].split('/')[2]
            problem_name = problem_no + problem_type + anchorTag.get_text().strip()
    print(problem_name)
    
    final_url = SUBMISSION_BASE_URL + '/' + problem_no + '/submission/' + id
    soup = fetch_data(final_url)
    code_area = soup.find('pre')
    code = []
    if code_area is None:
        print(problem_name , final_url)
        return
    for line in code_area:
        code.append(line)
    save_local(problem_no , problem_name , code)
    file.write(id+'\n')



def find_accepted_solutions(soup, list_of_ids, file):
    """
	Find the accepted solutions
	"""
    sol_table = soup.find("table", {"class": "status-frame-datatable"})
    rows = sol_table.find_all("tr")
    cnt = 0
    for row in rows:
        if cnt == 0:
            cnt += 1
            continue
        if (
            row.find("td", {"class": "status-cell"}).find("span")["submissionverdict"]
            == "OK"
        ):
            cnt += 1
            fetch_accepted_code(row, list_of_ids, file)
        # if cnt == 2:
        # 	break


def get_max_pageno(url):
    soup = fetch_data(url)
    page_indexes = soup.find_all("span", {"class": "page-index"})

    max_index = 1
    for page_index in page_indexes:
        max_index = page_index.get_text()
    return max_index


def main():
    handle_name = None
    handle_name = input("Enter Handle Name(Case Sensitive) : ")
    curr_dir = os.getcwd()
    req_dir = os.path.join(curr_dir , handle_name)

    if not os.path.exists(req_dir):
        os.mkdir(req_dir)
        filename = req_dir + '/idlist.txt'
        file = open(filename , 'w')
        file.close()
    os.chdir(req_dir)
    file = open('idlist.txt' , 'r')
    list_of_ids = []
    list_of_ids = file.readlines()
    file.close()

    final_url = BASE_URL + handle_name
    max_pages = get_max_pageno(final_url)

    file = open('idlist.txt' , 'a')

    for i in range(1 , int(max_pages)+1):
        print('Downloading Submissions from page ' , i , '/' , max_pages , sep = '')
        page_url = final_url + '/page/' + str(i)
        soup = fetch_data(page_url)
        find_accepted_solutions(soup , list_of_ids , file)

    file.close()


if __name__ == "__main__":
    main()