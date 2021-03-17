import spacy

nlp = spacy.load('en_core_web_sm')
sentences = [u"To start, we enjoyed sharing the manti, gulf prawns and lamb meatballs, hummus and muhammara.",
			u'The octopus, the tuna, the prawns, the ratatouille, the hummus, the mashed potatoes and the salads were all delicious!', 
			u'The hummus was decent but nothing special but the bread was delicious, only thing is there was not enough for the hummus so we ended up ordering a side of veggies ($3) to go with it.Chicken & Manchego Croquettes.',
			u'As a middle eastern guy I know a good shawarma sandwich when I see it.',
			u'I loved the soup of the day', 
			u'Lunch review.Falafel - 2/5Chefs plate:Spicy pork shawarma - 2/5Lamb leg skewer - 3/5Overall']

for sentence in sentences:
	print(sentence)
	doc = nlp(sentence)
	for chunk in doc.noun_chunks:
		print(chunk.text, chunk.root.text, chunk.root.dep_,
	          chunk.root.head.text)