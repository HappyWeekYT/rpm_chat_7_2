from random import randint

questions = list(range(1, 14))

for name in ['Сарибекян','Ларин','Веренев','Величко']:
    print(name)
    print(questions.pop(randint(0, len(questions)-1)))
    print(questions.pop(randint(0, len(questions)-1)))