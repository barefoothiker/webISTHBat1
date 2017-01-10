#!/usr/local/bin/perl 

use DBI;
use Time::Local;



$DEBUG = 2;


$ADMINID      = $ARGV[5];
$SITEID       = $ARGV[0];
$ANSNUM       = $ARGV[1];
$PROTOCOL     = $ARGV[2];
$INSTRUMENTID = $ARGV[3];
$DIAGNOSIS    = $ARGV[4];

if ( @ARGV < 6 ) {
    die "Usage: [SITEID] [TEXT/NUM] [PROTOCOL] INSTRUMENTID DIAGNOSIS ADMINID\n";
}
$dateout = `date "+%m%d%Y"`;
chomp $dateout;

$dbh;
if ($0 =~ /BATreports/){
	#$OUTFILE=$dateout.$SITEID.$ANSNUM.$PROTOCOL.$INSTRUMENTID.".xls";
	$OUTFILE =
  	"/tmp/" . $dateout . $SITEID . $ANSNUM . $PROTOCOL . $INSTRUMENTID . "_bat.xls";
	#$LOGFILE=$dateout.$SITEID.$ANSNUM.$PROTOCOL.$INSTRUMENTID.".log";
	$LOGFILE =
  	"/tmp/" . $dateout . $SITEID . $ANSNUM . $PROTOCOL . $INSTRUMENTID . "_bat.log";
  	
  	$dbh = DBI->connect( 'dbi:mysql:batwebapp', 'prat_admin', 'django_admin' );
  	$BATFLAG=1;
  
}elsif ($0 =~ /PRIreports/){
	#$OUTFILE=$dateout.$SITEID.$ANSNUM.$PROTOCOL.$INSTRUMENTID.".xls";
	$OUTFILE =
  "/tmp/" . $dateout . $SITEID . $ANSNUM . $PROTOCOL . $INSTRUMENTID . "_pri.xls";
  #$LOGFILE=$dateout.$SITEID.$ANSNUM.$PROTOCOL.$INSTRUMENTID.".log";
	$LOGFILE =
  "/tmp/" . $dateout . $SITEID . $ANSNUM . $PROTOCOL . $INSTRUMENTID . "_pri.log";
  
  $dbh = DBI->connect( 'dbi:mysql:pratwebapp', 'prat_admin', 'django_admin' );
	$PRIFLAG=1;
}
print "OUT $OUTFILE log $LOGFILE\n";
open( OUT, ">$OUTFILE" ) or die "Can't open file $OUTFILE \n";
open( LOG, ">$LOGFILE" ) or die "Can't open file $OUTFILE \n";
print LOG "Calling program...$0\n";
print LOG "
admin.....$ADMINID
siteid....$SITEID
textEn....$ANSNUM
protocol..$PROTOCOL
instrum...$INSTRUMENTID
diag......$DIAGNOSIS
";



my %ANS;

my (%TimeStamp) = getTimeStamp();
#my (%AGE)       = getAge($QIDAge);


my (%Pid2Ans);
my (%Pid2AnsId);
my (%Ans2num);    #hash of array to store all possible text-answers per question
my (%Quest2Sec);  #get sectionanme from qid
my (%isMultiple); #get multiple events questions
my (%Quest2Text); #get question text from question id

# populate hash HASH{aid}=anstext
my (%AID2TEXT)=getId2Ans();
# populate Quest2Text hash Quest2Text {qid}=qtext according to  input instrumentid
# populate idlist with qids according to input instrumentid
my (@idlist) = getQText();

print LOG "IDLIST @idlist\n";

# sort answers according to questions, assign numeric value for stats
#ans2num();

# FIX THIS!!!!!!!!!!!! should be dynamic
if ($PRIFLAG>0){
	(@idlistMult) = (
    2,   3,   4,   5,   8,   9,   11,  54,  55,  56,  57,  58,  59,  60,
    61,  62,  71,  72,  74,  87,  88,  121, 122, 123, 125, 126, 127, 129,
    131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 143, 144, 145, 146,
    147, 148, 149, 158, 166, 180, 193, 196, 197, 201, 206, 207, 215, 216,
    217, 218, 219, 220, 222, 223, 224, 225, 227, 236, 239, 266, 267, 273,
    274, 275, 276, 277, 278, 279, 280, 281, 283, 297, 304, 305, 306, 307,
    308, 310, 312, 319, 320, 321, 322, 327, 328, 329, 337, 101, 102, 130,
    150, 156, 164, 212, 242, 245, 248, 282, 315, 316, 183, 13, 14, 15
);
} elsif ($BATFLAG>0){
	(@idlistMult) = (53,54,55,56,60,61,62,63);
} else {@idlistMult; }

foreach my $k (@idlistMult) { $isMultiple{$k} = 1; }

# from Rank.xls file get rank for each answer
# populate $Ans2num{$questid}{$atext} = $rank;
#ans2num_v2();
#get_AnsRank();


if ($ANSNUM > 0 ) {
	get_AnsRank();
}
quest2sec();
 
# get hash of qid as keys and all possible answers as arrays
(%Q2A) = qid2aid();    ##defined in .pm

#
# populate hash of hashes HASH {pid}{qid}=anstext
#
($ResultsRef)= populateAnsHash ();

# Get total scores per questionnare per upin
if ($BATFLAG>0){
 %SCORE=get_score();
}
####################

$name = getSite();
$date = `date`;
print OUT "$date";



###############End ans per patient hash Pid2Ans
# Printing...
# Print qids as column titles
print OUT "\t\t\t\t";
for my $qid (@idlist) {
    if ( defined $isMultiple{$qid} ) {
        ##print OUT "MULT $qid\t";
        my $counter = @{ $Q2A{$qid} };
        for ( $i = 0 ; $i < $counter ; $i++ ) {
            print OUT "MULT $qid\t";
        }
    }
    else {
        print OUT "$qid\t";
    }
}
print OUT "\n";
print OUT "\t\t\t\t";
for my $qid (@idlist) {
    if ( defined $isMultiple{$qid} ) {
        ##print OUT "MULT $qid\t";
        my $counter = @{ $Q2A{$qid} };
        for ( $i = 0 ; $i < $counter ; $i++ ) {
            print OUT "$Quest2Sec{$qid}\t";
        }
    }
    else {
        print OUT "$Quest2Sec{$qid}\t";
    }
}
print OUT "\n";
## Print column names (actual questions)
print OUT "PID\tSiteID\tAdmin\tPriTime\t";
for my $qid (@idlist) {
    my ($quest) =     $Quest2Text{$qid};

    chomp $quest;
    $quest =~ s/\n/ /;
    $quest =~ s/\r//g;
	
    if ( defined $isMultiple{$qid} ) {
        ##print OUT "MULT $qid\t";
        my $counter = @{ $Q2A{$qid} };
        for ( $i = 0 ; $i < $counter ; $i++ ) {
            print OUT "$quest\t";
        }
    }
    else {
        print OUT "$quest\t";
        print LOG "..$quest...\n";
    }
}
print OUT "SCORE";
print OUT "\n";

#
# MULTiPLe print all possible answer choices for each question
#
print OUT "\t\t\t\t";
for my $qid (@idlist) {
    if ( defined $isMultiple{$qid} ) {
        foreach my $m ( @{ $Q2A{$qid} } ) {
            my $theoranstext = getAText($m);
            print OUT "$theoranstext\t";

            #print "QID $qid ARRAY @{ $Q2A{$qid} } ...ANSTEXT $anstext\n";
        }
    }
    else { print OUT "\t"; }
}
print OUT "\n";
#
# Print answers
#
foreach my $p_id ( sort keys %Pid2Ans ) {
    my ($admin) = getAdminId($p_id);
    if ( $DEBUG > 0 ) {
        print "DEBUGPID $p_id \t$SITEID\tadmin...$admin\n";
    }
    print OUT "PID $p_id \t$SITEID\t$admin\t";
    print OUT "$TimeStamp{$p_id}\t";
    #print OUT "$AGE{$p_id}\t";
    #print OUT "$calAGE{$p_id}\t";

    for my $qid (@idlist) {
    	
    	#
    	# Multiple Inst answers
    	#
        if ( defined $isMultiple{$qid} ) {
            my (%Q2AIns) = getMult2( $p_id, $qid );

            foreach my $m ( @{ $Q2A{$qid} } ) {
                my $anstext = $Q2AIns{$qid}{$m};
				if ($DEBUG > 0){
				print LOG "id $qid..$p_id...AID $m....ANSTEXT ANS $Q2AIns{$qid}{$m}...ANSTEXT $anstext.. num $Ans2num{$qid}{$anstext}...\n";
				}
				#
				# Print ranks
				#
                if ( $ANSNUM > 0 ) {
                    if ( exists $Ans2num{$qid}{$m} && exists $Q2AIns{$qid}{$m} ) {
                        print OUT "$Ans2num{$qid}{$m}\t";
                    }
                    else { print OUT "\t"; }

                }
                else { print OUT "$anstext\t"; }

            }
        #
        # Regular answers 
        #
        } else {

            if ( exists $Pid2Ans{$p_id}{$qid} ) {
                #
                # print OUT rank only if there are no concat instances for multiple-event questions
                #
                if ( $ANSNUM > 0 ) {
                    my $ansId = $Pid2AnsId{$p_id}{$qid};

					print LOG "TEST $p_id $Pid2Ans{$p_id}{$qid}..QID $qid..ANSid $ansId....ANS2NUM  $Ans2num{$qid}{$ansId} \n";
                    if ( exists $Ans2num{$qid}{$ansId} ) {
                        	if ($Ans2num{$qid}{$ansId} !~ /Freetext/){
                     		print LOG "loging ..id $p_id.. $Ans2num{$qid}{$ansId} line1\n";
                            print OUT "$Ans2num{$qid}{$ansId}\t";
                        	} else {
                        	print OUT "$Pid2Ans{$p_id}{$qid} \t";	
                        		print LOG "loging ..id $p_id.. $Ans2num{$qid}{$ansId} lineFREE\n";
                        	}
                        ## if the answer exists but no numeric rank for answertext - print OUT actual freetext
                    }
                    else {
                        #print OUT " $Pid2Ans{$p_id}{$qid} \t";
                    }
                }
                else {
                    ##print OUT answer column
                    print OUT " $Pid2Ans{$p_id}{$qid} \t";
                    print LOG "loging id $p_id...$Pid2Ans{$p_id}{$qid} line2\n ";	
                }
                ##if the answer does not exist for particular pid
            }
            else {
                ## if the question was not answered for a particular pid:
                ## for specific questions (301,302,303-aspirin)-print OUT rank or NULL
                if (   $qid eq '301'
                    || $qid eq '302'
                    || $qid eq '303'
                    || $qid eq '305'
                    || $qid eq '306' )
                {
                    if ( $ANSNUM > 0 ) {
                        print OUT "$Ans2num{$qid}{'NULL'}\t";
                        print LOG "loging id $p_id.. $Ans2num{$qid}{'NULL'} line3\n";
                    }
                    else { print OUT "NULL\t"; }
                }
                else {
                    print OUT "\t";
                }
            }
        }
    }
    ################################
    #	print score  for BAT
    print OUT $SCORE{$p_id} if exists $SCORE{$p_id};
    print OUT "\n";
}

#################
## getQID
#################
sub getQID {

    my ( $q, $secid ) = @_;
    my @id;
	my $sql;

if ($BATFLAG > 0){
	$sql = "
select distinct p.id
from  bat_question p, bat_instrumentsection pq
where p.text LIKE \"$q%\"
and p.instrumentsection_id like '$secid'
and pq.instrument_id=$INSTRUMENTID
";
}else {
	   $sql = "
select distinct p.id
from  prat_question p, prat_instrumentsection pq
where p.text LIKE \"$q%\"
and p.instrumentsection_id like '$secid'
and pq.instrument_id=$INSTRUMENTID
";
	
}
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";
    while ( @row = $sth->fetchrow_array ) {

        #print OUT "$row[0]\n" ;
        push( @id, $row[0] );
    }

    return (@id);
}


# populate global hash Quest2Text {qid}=qtext
sub getQText {
    my @idlist;
    my $sql;
    
    if ($BATFLAG > 0){
    $sql = "
SELECT q.id,  q.text
FROM bat_question q, bat_instrumentsection s
WHERE q.instrumentsection_id = s.id
and s.instrument_id=$INSTRUMENTID
ORDER BY s.sequence, q.instrumentsection_id, q.sequence";
    } else {
    	    $sql = "
SELECT q.id,  q.text
FROM prat_question q, prat_instrumentsection s
WHERE q.instrumentsection_id = s.id
and s.instrument_id=$INSTRUMENTID
ORDER BY s.sequence, q.instrumentsection_id, q.sequence";
    	
    }  
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";

    while ( @row = $sth->fetchrow_array ) {
        my $qid = $row[0];
        my $quest=$row[1];
        $Quest2Text{$qid} = $quest;
        push( @idlist, $qid );
    }
   return(@idlist);
}



sub  get_AnsRank{
my $sql;
my $rankname;
 if ($BATFLAG>0){	
 $sql="SELECT question_id , answer_id ,  rank
FROM bat_rank
WHERE instrument_id=$INSTRUMENTID";
} elsif ($PRIFLAG>0){


   if ($ANSNUM == 1){
                $rankname="rank";
        } elsif ($ANSNUM==2){
                $rankname="bin";
        }
  $sql="SELECT question_id , answer_id ,  rank
FROM    prat_rank
WHERE instrument_id=$INSTRUMENTID
AND rankname =\"$rankname\"";
print LOG "RANKsql $sql \n";
}
  $sth = $dbh->prepare($sql);
  $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";   
    while ( my @row = $sth->fetchrow_array ) {
    	my $questid=$row[0];
    	my $aid=$row[1];
   		my $rank=$row[2];		
    	   	$Ans2num{$questid}{$aid} = $rank;
    	
    	print LOG "RANK q $questid, a $aid, r $rank....$Ans2num{$questid}{$aid} is rank....\n ";
    }
}
#########################
##---populateAnsHash---##
## get answe#
#########################

sub populateAnsHash {
    #my ($id) = @_;

    %checkMax; #?Is it old variable?
     my %HASH;
	my $sql;
	if ($BATFLAG>0){
     $sql = "
SELECT  distinct a.upin_id , qa.text, qa.id , qi.id , qi.question_id, e.text
FROM  bat_administration a, bat_upin u, bat_questionanswer qa, bat_questionanswerinstance qi
LEFT JOIN bat_fillintheblank e ON qi.id = e.fills_id
WHERE qi.administration_id = a.id
AND qi.instrument_id = a.instrument_id
AND qa.id=qi.answer_id
AND u.id=a.upin_id
AND a.instrument_id=$INSTRUMENTID
AND a.site_id=$SITEID
AND u.study_id=$PROTOCOL";
	}else {
		 $sql = "
SELECT  distinct a.upin_id , qa.text, qa.id , qi.id , qi.question_id, e.text
FROM  prat_administration a, prat_upin u, prat_questionanswer qa, prat_questionanswerinstance qi
LEFT JOIN prat_fillintheblank e ON qi.id = e.fills_id
WHERE qi.administration_id = a.id
AND qi.instrument_id = a.instrument_id
AND qa.id=qi.answer_id
AND u.id=a.upin_id
AND a.instrument_id=$INSTRUMENTID
AND a.site_id=$SITEID
AND u.study_id=$PROTOCOL";
	}
if ($ADMINID eq '' || $ADMINID eq 'Select') {
	#do nothing, select all? for now
} else {
$sql .= " AND a.instrumentadministrator_id=$ADMINID";
}

#
# 1. DIAGNOSIS selected
# only valid for BHQ questionnaire!!!
# if insId(bhq)=1 and diagnosis selected not None or "select.." (none=1)
# Were you told that you had any of the following conditions? (Select all that apply) 
# qid=8
#

my $diagSql="
AND a.upin_id IN (
SELECT  distinct a.upin_id 
FROM prat_questionanswerinstance qi, prat_administration a
WHERE qi.administration_id = a.id
AND qi.instrument_id = a.instrument_id
AND qi.question_id =8
AND qi.answer_id =$DIAGNOSIS
)";
#
# NO DIAGNOSIS (None) selected
# Have you ever been told you have a bleeding disorder? (qid=6, answer 'No' aid=2)
#
my $diagNotSql="
AND a.upin_id IN (
SELECT  distinct a.upin_id 
FROM prat_questionanswerinstance qi, prat_administration a
WHERE qi.administration_id = a.id
AND qi.instrument_id = a.instrument_id
AND qi.question_id =6
AND qi.answer_id =2
)";
if ($DIAGNOSIS > 1 && $INSTRUMENTID == 1 && $PRIFLAG > 0) {
	$sql .= $diagSql;
} elsif ($DIAGNOSIS == 1 && $INSTRUMENTID == 1 && $PRIFLAG > 0) {
	$sql .= $diagNotSql;	
} elsif ($DIAGNOSIS =~ /Select/){
	#?
}


#    if ( $DEBUG > 0 ) {
        print LOG "getQ....$sql\n";
#    }
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";

    my $flag = 0;
    while ( my @row = $sth->fetchrow_array ) {
        
        my $pid    = $row[0];
        my $ansid  = $row[2];
        my $instid = $row[3];
        my $ans    = $row[1];
		my $qid     = $row[4];
		my $fans    = $row[5]; ##fillinthe blank answer
	
		if ($fans  ne ''){
                        $ans=$fans;
		}
		$HASH {$pid}{$qid} = $ans;
		$Pid2AnsId {$pid}{$qid} = $ansid;
		#if ($DEBUG >0){ print LOG "PopulateHash...$HASH {$pid}{$qid} = $ans\n";}
		push @{ $Results{$pid}{$qid} }, $ansid ;
	
    }    #while

 
%Pid2Ans=%HASH; 
    return (\%Results);

}    #sub

##################
#	sub get_score
# 	for BAT, assigned scores per each section added to get a final score per questionaire
sub get_score{
my %SCORE;
my $sql;

if ($BATFLAG>0){
$sql="SELECT SUM( s.score ) , a.upin_id
FROM bat_sectionscore s, bat_administration a
WHERE s.administration_id = a.id
GROUP BY a.id";	
}
	$sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";

    
    while ( my @row = $sth->fetchrow_array ) {
    	my $sum=$row[0];
    	my $upin=$row[1];
    	$SCORE{$upin}=$sum;
    }
    return (%SCORE);
}

sub getMult2 {
	my %Q2AIns; #(question to answer instance)
	my ( $pid, $qid )=@_;
	#push @{ $Results{$pid}{$qid} }, $ansid ;
	 
	 foreach my $aid ( @{ $ResultsRef->{ $pid }{ $qid } } ) {
		print LOG "ANSWER $AID2TEXT{$aid} aid..$aid...question $qid...upin..$pid\n ";
            	$Q2AIns{$qid}{$aid}=$AID2TEXT{$aid};
            }   
	return (%Q2AIns);
}
####################################
###
## get hash of qid as keys and all possible answers as arrays 
## input file extracted from ds9 sql query and saved

sub qid2aid{
	my %Q2A;
	my $SQL;
if ($BATFLAG>0){
$SQL="SELECT question_id qid, questionanswer_id aid
FROM bat_question_answers";
} else {
	$SQL="SELECT question_id qid, questionanswer_id aid
FROM prat_question_answers";
}
$sth = $dbh->prepare($SQL);
    $sth->execute
      || die "Could not execute SQL statement $SQL ... maybe invalid?";

    while ( @row = $sth->fetchrow_array ) {
    	my $qid=$row[0]; 
    	my $aid=$row[1];
    	push @{ $Q2A {$qid} }, $aid;
    }
    return(%Q2A);
}
sub getAText {
    my ($id) = @_;
    my $results;
    my $sql;
    if ($BATFLAG>0){
    $sql = "select  text from  bat_questionanswer where id=$id";
    } else {
    	$sql = "select  text from  prat_questionanswer where id=$id";
    }
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";

    while ( @row = $sth->fetchrow_array ) {
        $results = $row[0];
    }
    return ($results);
}
sub getId2Ans {
    
    my %AnsId2Text;
    my $sql;
    if ($BATFLAG>0){
    $sql = "select  text, id from  bat_questionanswer";
    } else {
    	$sql = "select  text, id from  prat_questionanswer";
    }
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";

    while ( @row = $sth->fetchrow_array ) {
    	my $atext=$row[0];
    	my $aid=$row[1];
        $AID2TEXT{$aid} = $atext;
    }
    return (%AID2TEXT);
}



#################
## getTimeStamp
##--returns timediff
#################
sub getTimeStamp {
    my %HASH;
	my $sql;
	if ($BATFLAG >0){
    $sql = "
select distinct upin_id,timediff(stop, start)
from bat_administration 
where site_id=$SITEID";
	} else {
		    $sql = "
select distinct upin_id,timediff(stop, start)
from prat_administration 
where site_id=$SITEID";
	}
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";
    while ( my @row = $sth->fetchrow_array ) {
        if ( $row[1] =~ /\:/ ) {
            my ( $h, $min, $s ) = split( /:/, $row[1] );
            if ( $h eq '00' ) {
                $HASH{ $row[0] } = $min;
            }
            elsif ( $h =~ /^0[1-2]*/ ) {
                $min = $min + ( $h * 60 );
                $HASH{ $row[0] } = $min;
                ##if report time is more then 3hr, report nothing
            }
            else { $HASH{ $row[0] } = ""; }
        }
        else {
            $HASH{ $row[0] } = "";

            # possible that stop time is NULL, then report nothing
        }
    }
    return (%HASH);
}
###############
## getAdminId
###############
sub getAdminId {
    my ($Pid) = @_;
    my $admin;
    my $sql;
    
    if ($BATFLAG>0){
     $sql = "
select distinct  p.instrumentadministrator_id 
from bat_administration p, bat_study_instruments pi where 
p.site_id=$SITEID
and pi.study_id = $PROTOCOL
and p.instrument_id=pi.instrument_id
and p.upin_id=$Pid";
    }else {
    	     $sql = "
select distinct  p.instrumentadministrator_id 
from prat_administration p, prat_study_instruments pi where 
p.site_id=$SITEID
and pi.study_id = $PROTOCOL
and p.instrument_id=pi.instrument_id
and p.upin_id=$Pid";
    }
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";
    while ( ($n) = $sth->fetchrow_array() ) {
        $admin = $n;    ####### WHAT?????
    }
    if ( $DEBUG > 0 ) { print "ADMIN $admin...$sql...\n"; }
    return ($admin);

}
##################
## quest2sec
#################
sub quest2sec {

    my (@results);
    my $sql ;

if ($BATFLAG>0){
$sql= "
SELECT q.id,  s.id, s.name
FROM bat_question q, bat_instrumentsection s
WHERE q.instrumentsection_id = s.id
AND s.instrument_id=$INSTRUMENTID
ORDER BY s.sequence, q.instrumentsection_id, q.sequence";

} else {
$sql= "
SELECT q.id,  s.id, s.name
FROM prat_question q, prat_instrumentsection s
WHERE q.instrumentsection_id = s.id
AND s.instrument_id=$INSTRUMENTID
ORDER BY s.sequence, q.instrumentsection_id, q.sequence";
}
print LOG "$sql\n";
    $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";

    while ( @row = $sth->fetchrow_array ) {
        my $sid = $row[1];
        my $qid     = $row[0];
        push( @results, $qid );
        $Quest2Sec{$qid} = $sid;
    }
    
}

################
## getSite
#################
sub getSite {
    my $name;
    my $sql;
    if ($BATFLAG>0){
    $sql = "select distinct name
from bat_site
where id=$SITEID";
    } else {
            $sql = "select distinct name
from prat_site
where id=$SITEID";
    }
    my $sth = $dbh->prepare($sql);
    $sth->execute
      || die "Could not execute SQL statement $sql ... maybe invalid?";
    while ( ($n) = $sth->fetchrow_array() ) {
        $name = $n;    ####### WHAT?????
    }
    return ($name);
}



