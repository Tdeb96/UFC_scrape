library(tidyverse)

#Import datasets
fights <- read_csv("~/Documents/UFC_project/Data/20201207fights.csv")

#Get the stopage methods and count per year
yearly_stats <- fights %>% group_by(Year, Finish_method) %>% summarize(occurances = n()) %>% ungroup()
yearly_stats$Finish_method <- as.factor(yearly_stats$Finish_method)
#Unionize the categories
unique(yearly_stats$Finish_method)
new_cats <- c("KO/TKO", "Submission", NA, "Decision", NA, 
              "KO/TKO", "Decision", "Decision", 
              "Other", NA, "KO/TKO", "Decision", "Submission", NA, 
              "Other", NA)
key <- data.frame(old = unique(yearly_stats$Finish_method), new = new_cats)
yearly_stats <- left_join(yearly_stats, key, by =c("Finish_method" = "old")) %>% select(c(1,3,4)) %>% drop_na()

#get the percentages of the finishes
yearly_stats <- yearly_stats %>% group_by(Year, new) %>% summarize(occurances = sum(occurances)) %>% ungroup()
yearly_stats <- group_by(yearly_stats, Year) %>% mutate(percent = occurances/sum(occurances))

write.csv(yearly_stats, "~/Documents/UFC_project/Data/Yearly_stats.csv")
