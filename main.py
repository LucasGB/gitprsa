from SentiCR.SentiCR import  SentiCR
import pickle
from git import *
import os
import pandas as pd
import random

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
    polarities = []

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
        #print(sent+"\n Score: "+str(score))
        polarities.append(score)

    return polarities


if __name__ == '__main__':
    #classify(sentences)
    repositories = []

    # Load list of repositories to mine
    with open('repositories/repositories.txt', 'r') as file:
      repositories = file.read().splitlines()
    
    pull_requests = []

    for repository in repositories:
      full_name = repository.split('/')

#      get_closed_pull_request_numbers_from_repo(repository)

      with open('repositories/{}_{}/{}_{}_pull_request_numbers.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1]), 'r') as file:
           for line in file.readlines():
            pull_requests.append(line)

#      for pull_request in pull_requests:
#         status = verify_acceptance(repository, pull_request)

#        if status == True:
#          with open('repositories/{}_{}/{}_{}_accepted_prs.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1]), 'a') as output:
#            output.write(pull_request)
#        elif status == False:
#          with open('repositories/{}_{}/{}_{}_rejected_prs.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1]), 'a') as output:
#            output.write(pull_request)
#        else:
#            continue

      accepted_prs = []
      rejected_prs = []

      with open('repositories/{}_{}/{}_{}_accepted_prs.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1]), 'r') as file:
        for line in file.readlines():
          accepted_prs.append(line)

      print len(accepted_prs)
#      with open('repositories/{}_{}/{}_{}_rejected_prs.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1]), 'r') as file:
#        for line in file.readlines():
#          rejected_prs.append(line)
#      print len(rejected_prs)
      sample_percentage = 0.2

      sample_accepted_prs = random.sample(accepted_prs, int(len(accepted_prs) * sample_percentage))
#      sample_rejected_prs = random.sample(rejected_prs, int(len(rejected_prs) * sample_percentage))

#      print len(sample_accepted_prs)
#      print len(sample_rejected_prs)

      with open('repositories/{}_{}/{}_{}_sampled_{}_accepted_prs.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1], int(sample_percentage * 100)), 'a') as output:
        for pr in sample_accepted_prs:
          output.write(pr)

#      with open('repositories/{}_{}/{}_{}_sampled_{}_rejected_prs.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1], int(sample_percentage * 100)), 'a') as output:
#        for pr in sample_rejected_prs:
#          output.write(pr)

      '''
      AP = Accepted and merged, mostly positive comments
      AN = Accepted and merged, mostly negative comments
      RP = Rejected and closed, mostly positive comments
      RN = Rejected and closed, mostly negative comments
      AT = Accepted and merged, tie between positive and negative comments
      RT = Rejected and closed, tie between positive and negative comments
      '''
      AP = 0
      RP = 0
      AN = 0
      RN = 0
      AT = 0
      RT = 0

      for pr in sample_accepted_prs:
        review_comments = get_review_comments_from_pull_request(repository, pr)
        merged = verify_merged_at_attr_from_pull_request(repository, pr)

        review_polarities = classify(review_comments)

        print review_polarities[0]

        n_positive_comments = review_polarities.count(0)
        n_negative_comments = review_polarities.count(-1)

        print 'POS: ',n_positive_comments
        print 'NEG: ',n_negative_comments

        if n_positive_comments > n_negative_comments and merged == True:
          AP += 1
        elif n_positive_comments > n_negative_comments and merged == False:
          RP += 1
        elif n_negative_comments > n_positive_comments and merged == True:
          AN += 1
        elif n_negative_comments > n_positive_comments and merged == False:
          RN += 1
        elif n_positive_comments == n_negative_comments and merged == True:
          AT += 1
        else:
          RT += 1

      '''
      for pr in sample_rejected_prs:
        review_comments = get_review_comments_from_pull_request(repository, pr)
        merged = verify_merged_at_attr_from_pull_request(repository, pr)

        review_polarities = classify(review_comments)

        print review_polarities[0]

        n_positive_comments = review_polarities.count(0)
        n_negative_comments = review_polarities.count(-1)

        print 'POS: ',n_positive_comments
        print 'NEG: ',n_negative_comments

        if n_positive_comments > n_negative_comments and merged == True:
          AP += 1
        elif n_positive_comments > n_negative_comments and merged == False:
          RP += 1
        elif n_negative_comments > n_positive_comments and merged == True:
          AN += 1
        elif n_negative_comments > n_positive_comments and merged == False:
          RN += 1
        elif n_positive_comments == n_negative_comments and merged == True:
          AT += 1
        else:
          RT += 1
      '''
      print AP
      print RP
      print AN
      print RN
      print AT
      print RT

      with open('repositories/{}_{}/{}_{}_result.txt'.format(full_name[0], full_name[1], full_name[0], full_name[1]), 'w') as output:
        output.write('AP = {}\nRP = {}\nAN = {}\nRN = {}\nAT = {}\nRT = {}'.format(AP, RP, AN, RN, AT, RT))

    print 'Finished.'