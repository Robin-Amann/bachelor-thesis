str = ["i like yeah i like the relaxed atmosphere and um would right um well  um it's just you can just really relax and talk with your spouse if you have a spouse", "I like the relaxed atmosphere. Well, you can just really relax and talk with your spouse if you have a spouse."]



for s in str :
    s = s.upper().replace(" ", "|").replace(".", "").replace(",", "").replace("?", "")
    print (s)