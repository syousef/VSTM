#to run file, type source("/Users/sheremat/Documents/aricept_vstm/preliminary8_ANOVA.R",echo=T)


#Have R read data from a tab delimited file (here made in excel #and saved as tab delimited text)

Exp1_data <-read.table("/Users/saharyousef/Desktop/vstm_code/ANOVA_data.txt",header=T)

summary(Exp1_data)#

#HERE IS THE EZ way of doing an ANOVA

psos_anova = ezANOVA(
    data = Exp1_data[Exp1_data$ENCODING=='short',]
    , dv = .(DPRIME)#depedent variable
    , wid = .(SUBJ)
    , within = .(SS,TSTIM,PILL)
    , between = .(ORDER)
)

print(psos_anova)
