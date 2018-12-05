from SentiCR.SentiCR import  SentiCR
import pickle
from git import *
import os
import pandas as pd

#All examples are acutal code review comments from Go lang

sentences=["I'm not sure I entirely understand what you are saying. "+\
           "However, looking at file_linux_test.go I'm pretty sure an interface type would be easier for people to use.",
           "I think it always returns it as 0.",
           "If the steal does not commit, there's no need to clean up _p_'s runq. If it doesn't commit,"+\
             " runqsteal just won't update runqtail, so it won't matter what's in _p_.runq.",
           "Please change the subject: s:internal/syscall/windows:internal/syscall/windows/registry:",
           "I don't think the name Sockaddr is a good choice here, since it means something very different in "+\
           "the C world.  What do you think of SocketConnAddr instead?",
           "could we use sed here? "+\
            " https://go-review.googlesource.com/#/c/10112/1/src/syscall/mkall.sh "+\
            " it will make the location of the build tag consistent across files (always before the package statement).",
           "Is the implementation hiding here important? This would be simpler still as: "+\
          " typedef struct GoSeq {   uint8_t *buf;   size_t off;   size_t len;   size_t cap; } GoSeq;",
           "Make sure you test both ways, or a bug that made it always return false would cause the test to pass. "+\
        " assertTrue(Testpkg.Negate(false)); "+\
        " assertFalse(Testpkg.Negate(true)); +"\
        " If you want to use the assertEquals form, be sure the message makes clear what actually happened and " +\
        "what was expected (e.g. Negate(true) != false). ",
        "(^-^)",
        "This is the worst code snippet I have ever seen. You suck.",
        "I don't think this is what I'm looking for.",
        "This doesn't work."]


def classify(sentences):

    saved_SentiCR_model = 'classifier_models/SentiCR_model.sav'
    
    if(os.path.exists(saved_SentiCR_model)):
      sentiment_analyzer = pickle.load(open(saved_SentiCR_model, 'rb'))
      print 'Loaded SentiCR model'
    else:
      sentiment_analyzer = SentiCR.SentiCR()
      pickle.dump(sentiment_analyzer, open(saved_SentiCR_model, 'wb'))
      print 'Saved model to file'

    for sent in sentences:
        score = sentiment_analyzer.get_sentiment_polarity(sent)
        print(sent+"\n Score: "+str(score))


if __name__ == '__main__':
    #classify(sentences)
    repositories = []

    # Load list of repositories to mine
    with open('repositories/repositories.txt', 'r') as file:
      repositories = file.read().splitlines()
    
    pull_requests = []

    for repository in repositories:
      pull_requests = get_closed_pull_request_numbers_from_repo(repository)

    
    print pull_requests
    

    ###########
    #pr = [str(34212), str(34227), str(34403)]
    #a = filter_by_presence_of_changed_files(pr)
    #print len(a)

#    a = filter_by_presence_of_changed_files(pull_requests)
#    print len(a)

    #review_comments = get_review_comments_from_pull_request(str(34227))
    
    #classify(review_comments)  