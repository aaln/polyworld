import counterpush_hosted as runner
from victory_counterpush import STUDY

if __name__=='__main__':
    runner.STUDY=STUDY
    runner.PREFIX='aaron-gota-ir-victory'
    runner.CHANGE='Release red defenders after observed local victory: two visible enemy corpses, surviving allied group and no nearby living enemy hero. Class-separated rally; exact blue branch.'
    runner.main()
