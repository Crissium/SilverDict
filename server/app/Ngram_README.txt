= A trial of bi-directional n-grams based dictionary completion of user input (LIKE %input%)

For each key in the "entries" table we generate all n-grams (sequence of n consecutive characters,
typically n=3 or 4).

We use an auxiliary table to store the ngrams and the keys they match (each ngram usually matches
many keys of course).

Several methods were tried, on a 5 million entries dictionary db:

 - Store all (ngram,key) records. Creating the table is very very fast (minutes), but the result is
   very big (practically doubling the original dictionary table.

 - Store (ngram, keylist) records, where keylist is a comma-separated string list of all the keys
   containing the ngram.

 - Store (ngram, idxlist) records, where idxlist is a comma-separated string list of the "entries"
   table rowids for the corresponding keys. This is slightly more compact than the previous, with no
   significant performance penalty.

Creating the auxiliary table for the two last methods is slow: 15 minutes with 4-grams and 2 hours
with 3-grams on a decent laptop (Thinkpad T580).

The resulting db is approximately 16% bigger with 4-grams and 22% with 3-grams.

I also tried 5-grams, but the resulting db is barely smaller than for 4-grams (the generation is
faster though).

3-grams allow generating completions earlier (as soon as the user has typed 3 characters), but the
match lists at this step are so huge that I don't think that they are usable, so, given  the
very high generation time and higher space usage, using sequences of at least 4 characters seem
better. 

Expansion for both sequence sizes is very fast (a few dozen milliseconds on the same laptop), and
faster with 4-grams.

A size of 4 seems to be the right choice.

The code is very simple:

 - ngrams_common.py contains the ngram-generating function, the ngram size and the dictionary path.
 - ngrams_create.py creates and populates the ngrams table in an ngram-less dictionary db.
 - ngrams_expand.py takes a string parameter and expands it.
 
A few tests with ngramlen 3 and 4 follow. Note the typical huge size (2000) of the expansion of a 3
letters input for ngramlen==3

With this particular sequence, the resulting list becomes really usable when the user has entered 6
characters (result list size 15).


== Tests with ngramlen==4

$ time ./ngrams_expand.py nobl | wc -l
    241
real 0m0,036s  user 0m0,025s  sys 0m0,015s

$ time ./ngrams_expand.py nobli | wc -l
     50
real 0m0,041s  user 0m0,039s  sys 0m0,006s

$ time ./ngrams_expand.py noblig | wc -l
     15
real 0m0,035s  user 0m0,021s  sys 0m0,019s

$ time ./ngrams_expand.py nobliga 
KEY inobligality
KEY unobligatory
KEY concessionobligation
KEY gewinnobligation
KEY kassenobligation
KEY acquitsomebodyfromanobligation
KEY assumeanobligation
KEY releasedfromanobligation
KEY nonobligatory
KEY kassenobligation
real 0m0,035s  user 0m0,027s   sys 0m0,008s


== Tests with ngramlen== 3

$ time ./ngrams_expand.py nob | wc -l
   2077
real 0m0,039s  user 0m0,032s  sys 0m0,011s

$ time ./ngrams_expand.py nobl | wc -l
    241
real 0m0,037s  user 0m0,027s  sys 0m0,014s

$ time ./ngrams_expand.py nobliga
KEY inobligality
KEY unobligatory
KEY concessionobligation
KEY gewinnobligation
KEY kassenobligation
KEY acquitsomebodyfromanobligation
KEY assumeanobligation
KEY releasedfromanobligation
KEY nonobligatory
KEY kassenobligation
real 0m0,062s   user 0m0,054s  sys 0m0,009s
