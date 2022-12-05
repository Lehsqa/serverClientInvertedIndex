text_1 = "The big sharks of Belgium drink beer."
text_2 = "Belgium has great beer. They drink beer all the time."

for i in range(101, 2000):
    open(f"doc{i}", 'w').write(text_1 if i % 2 == 0 else text_2)
