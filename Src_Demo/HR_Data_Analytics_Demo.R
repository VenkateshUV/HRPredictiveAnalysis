#Importing the dataset to R
setwd("C:/Users/VenksUV/Desktop/6112 - SSDI/SSDI_PROJECT")
MFG10YearTerminationData <- read.csv("C:/Users/VenksUV/Desktop/6112 - SSDI/MFG10YearTerminationData.csv")
MYdataset <- MFG10YearTerminationData
library(plyr)
library(dplyr)
#What proportion of our staff are leaving?
StatusCount<- as.data.frame.matrix(MYdataset %>%
                                     group_by(STATUS_YEAR) %>%
                                     select(STATUS) %>%
                                     table())
StatusCount$TOTAL<-StatusCount$ACTIVE + StatusCount$TERMINATED
StatusCount$PercentTerminated <-StatusCount$TERMINATED/(StatusCount$TOTAL)*100
StatusCount
mean(StatusCount$PercentTerminated)

#Where are the terminations occurring?
#By Business Unit
library(ggplot2)
ggplot() + geom_bar(aes(y = ..count..,x =as.factor(BUSINESS_UNIT),fill = as.factor(STATUS)),data=MYdataset,position = position_stack())

#By Termination Type And Status Year
TerminatesData<- as.data.frame(MYdataset %>%
                                 filter(STATUS=="TERMINATED"))
ggplot() + geom_bar(aes(y = ..count..,x =as.factor(STATUS_YEAR),fill = as.factor(STATUS)),data=MYdataset,position = position_stack())

#By Status year and Termination Reason
ggplot() + geom_bar(aes(y = ..count..,x =as.factor(STATUS_YEAR),fill = as.factor(termreason_desc)),data=TerminatesData,position = position_stack())

#By Termination Reason and Department
ggplot() + geom_bar(aes(y = ..count..,x =as.factor(department_name),fill = as.factor(termreason_desc)),data=TerminatesData,position = position_stack())+
  theme(axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))

#How does Age and Length of Service affect termination?
library(caret)
## Loading required package: lattice
featurePlot(x=MYdataset[,6],y=MYdataset$STATUS,plot="density",auto.key = list(columns = 2))

featurePlot(x=MYdataset[,7],y=MYdataset$STATUS,plot="density",auto.key = list(columns = 2))

featurePlot(x=MYdataset[,18],y=MYdataset$STATUS,plot="density",auto.key = list(columns = 1))

#Age and Length of Service Distributions By Status
featurePlot(x=MYdataset[,6:7],y=MYdataset$STATUS,plot="box",auto.key = list(columns = 2))

library(rattle)
library(magrittr)
MYdataset
crv$seed
set.seed(crv$seed) 
MYnobs = nrow(MYdataset)
MYtrain = subset(MYdataset,STATUS_YEAR<=2014)
MYvalidate = NULL
MYtest = subset(MYdataset,STATUS_YEAR== 2015)

MYinput = c("age", "length_of_service",    "gender_full", "STATUS_YEAR", "BUSINESS_UNIT")

MYnumeric = c("age", "length_of_service", "STATUS_YEAR")

MYcategoric = c("gender_full", "BUSINESS_UNIT")

MYtarget = "STATUS"
MYrisk   = NULL
MYident   = "EmployeeID"
MYignore  = c("recorddate_key", "birthdate_key", "orighiredate_key", "terminationdate_key", "city_name", "gender_short", "termreason_desc", "termtype_desc","department_name","job_title", "store_name")
MYweights = NULL

MYTrainingData<-MYtrain[c(MYinput, MYtarget)]
MYTestingData<-MYtest[c(MYinput, MYtarget)]

library(rattle)
library(rpart, quietly=TRUE)
set.seed(crv$seed)

MYrpart = rpart(STATUS ~ .,
              data=MYtrain[, c(MYinput, MYtarget)],
              method="class",
              parms=list(split="information"),
              control=rpart.control(usesurrogate=0, 
                                    maxsurrogate=0))


fancyRpartPlot(MYrpart, main="Decision Tree MFG10YearTerminationData $ STATUS")


MYglm = glm(STATUS ~ .,
          data=MYtrain[c(MYinput, MYtarget)],
          family=binomial(link="logit"))

print(summary(MYglm))

VariableImportance = varImp(MYglm, scale = FALSE)

write.csv(VariableImportance, file = "FactorImportance.csv")

print(anova(MYglm, test="Chisq"))

slices <- c(50.094896, 39.737573 , 7.671146, 26.148156, 16.486490)
lbls <- c("age", "length_of_service", "gender_full", "STATUS_YEAR", "BUSINESS_UNIT")
pie(slices, labels = lbls, col = rainbow(length(slices)),main="Pie Chart")
library(plotrix)

age = MYdataset$age
STATUS = MYdataset$STATUS   
plot(STATUS, age,      
     xlab="STATUS",  
     ylab="age")

length_of_service = MYdataset$length_of_service
STATUS = MYdataset$STATUS   
plot(STATUS, length_of_service,      
     xlab="STATUS",  
     ylab="length_of_service")

gender_full = MYdataset$gender_full
STATUS = MYdataset$STATUS   
plot(STATUS, gender_full,      
     xlab="STATUS",  
     ylab="gender_full")

STATUS_YEAR = MYdataset$STATUS_YEAR
STATUS = MYdataset$STATUS   
plot(STATUS, STATUS_YEAR,      
     xlab="STATUS",  
     ylab="STATUS_YEAR")

BUSINESS_UNIT = MYdataset$BUSINESS_UNIT
STATUS = MYdataset$STATUS   
plot(STATUS, BUSINESS_UNIT,      
     xlab="STATUS",  
     ylab="BUSINESS_UNIT")

library("ggplot2")
ggplot(MYdataset, aes(age, as.numeric(STATUS)-1, color=gender_full)) +
  stat_smooth(method="glm", family=binomial, formula=y~x,
              alpha=0.2, size=2, aes(fill=gender_full)) +
  geom_point(position=position_jitter(height=0.03, width=0)) +
  xlab("Age") + ylab("Pr (STATUS)")


require(ggplot2)
ggplot(MYdataset, aes(age, as.numeric(STATUS)-1, color=gender_full)) +
  stat_smooth(method="loess", formula=y~x,
              alpha=0.2, size=2, aes(fill=gender_full)) +
  geom_point(position=position_jitter(height=0.03, width=0)) +
  xlab("Age") + ylab("Pr (STATUS)")


ggplot(MYdataset, aes(x=age, y=STATUS))+geom_point(size=2, alpha=0.4)+
  stat_smooth(method="loess", colour="blue", size=1.5)+
  xlab("age")+
  ylab("STATUS")+
  theme_bw()

qplot(x=age, y=STATUS, data = MYdataset)