from nltk.corpus import wordnet as wn

tension=['tense', 'shaky', 'on-edge', 'panicky', 'uneasy', 'restless', 'nervous', 'anxious', 'relaxed']
depression=['unhappy', 'sorry-for-things-done', 'sad', 'blue', 'hopeless', 'unworthy', 'discouraged', 'lonely', 'miserable', 'gloomy','desperate', 'helpless', 'worthless', 'terrified', 'guilty']
anger=['anger', 'peeved', 'grouchy', 'spiteful', 'annoyed', 'resentful','bitter', 'ready-to-fight','rebellious', 'deceived', 'furious','bad-tempered']
vigour=['lively', 'active', 'energetic', 'cheerful', 'alert','full of pep', 'carefree', 'vigorous']
fatigue=['worn-out', 'listless', 'fatigued', 'exhausted', 'sluggish','weary', 'bushed']
confusion=['confused', 'unable-to-concentrate', 'muddled', 'bewildered','forgetful', 'uncertain-about-things', 'efficient']

poms=tension+depression+anger+vigour+fatigue+confusion


final={}
flat_final = []
total=0
for word in poms:
	final[word] = []
	for s in wn.synsets(word):
		final[word].append(s)
		final[word]+=s.also_sees()
		final[word]+=s.similar_tos()
	total+=len(final[word])
	print "%s\n%s\n\n\n" % (word, final[word])

print total
