import csv


"""
Given maintenance spreadsheet as csv, make a repos file.
"""


class Repo:

    def __init__(self, org_repo, comaintainers):
        self.org, self.name = org_repo.split('/')
        self.comaintainers = comaintainers


    def as_yaml(self, indent='  '):
        return '\n'.join((
            f'{indent}{self.org}/{self.name}:' + (f'  # Co-maintainers: {", ".join(self.comaintainers)}' if self.comaintainers else ''),
            f'{indent}  type: git',
            f'{indent}  url: https://github.com/{self.org}/{self.name}.git'))


def main():
    other_people = ('wjwwood', 'ivanpauno', 'mjeronimo', 'jacobperron', 'clalancette', 'tfoote', 'mabelzhang', 'ahcorde', 'mjcarroll', 'cottsay', 'nuclearsandwich', 'hidmic', 'gbiggs', 'adityapande-1995', 'audrow', 'scpeters', 'External')

    my_repos = []

    with open('maintain.csv') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if row['sloretz']:
                comaintainers = []
                for person in other_people:
                    if row[person]:
                        comaintainers.append(person)
                my_repos.append(Repo(row['# Repo'], comaintainers))

    print('repositories:')
    for repo in my_repos:
        print(repo.as_yaml())


if __name__ == '__main__':
    main()
