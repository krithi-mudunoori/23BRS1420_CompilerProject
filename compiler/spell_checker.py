"""
Spelling Validator & Corrector — Compiler Phase 2 (Semantic Analysis)
Uses a dictionary loaded from an embedded word list and edit-distance
algorithms to detect misspellings and suggest corrections.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set

from .lexer import Token, TokenType


# ---------------------------------------------------------------------------
# Embedded core dictionary (~10 000 common English words subset)
# We generate this from a frequency list at import time; no external file needed.
# ---------------------------------------------------------------------------

_COMMON_WORDS: Set[str] = set()


def _build_dictionary() -> Set[str]:
    """Return a set of common English words.  We embed a compact list so the
    app has zero external data-file dependencies."""
    # fmt: off
    words = (
        "a,able,about,above,accept,according,account,across,act,action,"
        "activity,actually,add,address,administration,admit,adult,affect,"
        "after,again,against,age,agency,agent,ago,agree,agreement,ahead,"
        "air,all,allow,almost,alone,along,already,also,always,american,"
        "among,amount,analysis,and,animal,another,answer,any,anyone,"
        "anything,appear,apply,approach,area,argue,arm,around,arrive,art,"
        "article,as,ask,assume,at,attack,attention,attorney,audience,"
        "author,authority,available,avoid,away,baby,back,bad,bag,ball,"
        "ban,bank,bar,base,be,beat,beautiful,because,become,bed,before,"
        "begin,behavior,behind,believe,benefit,best,better,between,beyond,"
        "big,bill,billion,bit,black,blood,blue,board,body,bone,book,born,"
        "both,box,boy,break,bring,brother,budget,build,building,business,"
        "but,buy,by,call,camera,campaign,can,cancer,candidate,capital,car,"
        "card,care,career,carry,case,catch,cause,cell,center,central,"
        "century,certain,certainly,chair,chairman,challenge,chance,change,"
        "character,charge,check,child,children,choice,choose,church,citizen,"
        "city,civil,claim,class,clear,clearly,close,coach,cold,collection,"
        "college,color,come,commercial,common,community,company,compare,"
        "computer,concern,condition,conference,congress,consider,consumer,"
        "contain,continue,control,cost,could,country,couple,course,court,"
        "cover,create,crime,cultural,culture,cup,current,customer,cut,"
        "dark,data,daughter,day,dead,deal,death,debate,decade,decide,"
        "decision,deep,defense,degree,democrat,democratic,department,depend,"
        "describe,design,despite,detail,determine,develop,development,die,"
        "difference,different,difficult,dinner,direction,director,discover,"
        "discuss,discussion,disease,do,doctor,dog,door,down,draw,dream,"
        "drive,drop,drug,during,each,early,east,easy,eat,economic,economy,"
        "edge,education,effect,effort,eight,either,election,else,employee,"
        "end,energy,enjoy,enough,enter,entire,environment,environmental,"
        "especially,establish,even,evening,event,ever,every,everybody,"
        "everyone,everything,evidence,exactly,example,executive,exist,"
        "expect,experience,expert,explain,eye,face,fact,factor,fail,fall,"
        "family,far,fast,father,fear,federal,feel,few,field,fight,figure,"
        "fill,film,final,finally,financial,find,fine,finger,finish,fire,"
        "firm,first,fish,five,floor,fly,focus,follow,food,foot,for,force,"
        "foreign,forget,form,former,forward,four,free,friend,from,front,"
        "full,fund,future,game,garden,gas,general,generation,get,girl,"
        "give,glass,go,goal,god,good,government,great,green,ground,group,"
        "grow,growth,guess,gun,guy,hair,half,hand,hang,happen,happy,hard,"
        "have,he,head,health,hear,heart,heat,heavy,help,her,here,herself,"
        "high,him,himself,his,history,hit,hold,home,hope,hospital,hot,"
        "hotel,hour,house,how,however,huge,human,hundred,husband,idea,"
        "identify,if,image,imagine,impact,important,improve,in,include,"
        "including,increase,indeed,indicate,industry,information,inside,"
        "instead,institution,interest,interesting,international,interview,"
        "into,investment,involve,issue,it,item,its,itself,job,join,just,"
        "keep,key,kid,kill,kind,kitchen,know,knowledge,land,language,large,"
        "last,late,later,laugh,law,lawyer,lay,lead,leader,learn,least,"
        "leave,left,leg,legal,less,let,letter,level,lie,life,light,like,"
        "likely,line,list,listen,little,live,local,long,look,lose,loss,"
        "lost,lot,love,low,machine,magazine,main,maintain,major,majority,"
        "make,man,manage,management,manager,many,market,marriage,material,"
        "matter,may,maybe,me,mean,measure,media,medical,meet,meeting,"
        "member,memory,mention,message,method,middle,might,military,"
        "million,mind,minute,miss,mission,model,modern,moment,money,month,"
        "more,morning,most,mother,mouth,move,movement,movie,much,music,"
        "must,my,myself,name,nation,national,natural,nature,near,nearly,"
        "necessary,need,network,never,new,news,newspaper,next,nice,night,"
        "no,none,nor,north,not,note,nothing,notice,now,number,occur,of,"
        "off,offer,office,officer,official,often,oh,oil,ok,old,on,once,"
        "one,only,onto,open,operation,opportunity,option,or,order,"
        "organization,other,others,our,out,outside,over,own,owner,page,"
        "pain,painting,pair,paper,parent,part,particular,particularly,"
        "partner,party,pass,past,patient,pattern,pay,peace,people,per,"
        "perform,performance,perhaps,period,person,personal,phone,"
        "physical,pick,picture,piece,place,plan,plant,play,player,please,"
        "point,police,policy,political,politics,poor,popular,population,"
        "position,positive,possible,power,practice,prepare,present,"
        "president,pressure,pretty,prevent,price,private,probably,problem,"
        "process,produce,product,production,professional,professor,program,"
        "project,property,protect,prove,provide,public,pull,purpose,push,"
        "put,quality,question,quickly,quite,race,radio,raise,range,rate,"
        "rather,reach,read,ready,real,reality,realize,really,reason,"
        "receive,recent,recently,recognize,record,red,reduce,reflect,"
        "region,relate,relationship,religious,remain,remember,remove,"
        "report,represent,republican,require,research,resource,respond,"
        "response,rest,result,return,reveal,rich,right,rise,risk,road,"
        "rock,role,room,rule,run,safe,same,save,say,scene,school,science,"
        "scientist,score,sea,season,seat,second,section,security,see,seek,"
        "seem,sell,send,senior,sense,series,serious,serve,service,set,"
        "seven,several,shake,share,she,shoot,short,shot,should,shoulder,"
        "show,side,sign,significant,similar,simple,simply,since,sing,"
        "single,sister,sit,site,situation,six,size,skill,skin,small,"
        "smile,so,social,society,soldier,some,somebody,someone,something,"
        "sometimes,son,song,soon,sort,sound,source,south,southern,space,"
        "speak,special,specific,speech,spend,sport,spring,staff,stage,"
        "stand,standard,star,start,state,statement,station,stay,step,"
        "still,stock,stop,store,story,strategy,street,strong,structure,"
        "student,study,stuff,style,subject,success,successful,such,"
        "suddenly,suffer,suggest,summer,support,sure,surface,system,table,"
        "take,talk,task,tax,teach,teacher,team,technology,television,tell,"
        "ten,tend,term,test,than,thank,that,the,their,them,themselves,"
        "then,there,these,they,thing,think,third,this,those,though,"
        "thought,thousand,threat,three,through,throughout,throw,thus,time,"
        "to,today,together,tonight,too,top,total,tough,toward,town,trade,"
        "traditional,training,travel,treat,treatment,tree,trial,trip,"
        "trouble,true,truth,try,turn,tv,two,type,under,understand,unit,"
        "until,up,upon,us,use,usually,value,various,very,victim,view,"
        "violence,visit,voice,vote,wait,walk,wall,want,war,watch,water,"
        "way,we,weapon,wear,week,weight,well,west,western,what,whatever,"
        "when,where,whether,which,while,white,who,whole,whom,whose,why,"
        "wide,wife,will,win,wind,window,wish,with,within,without,woman,"
        "wonder,word,work,worker,world,worry,would,write,writer,wrong,"
        "yard,yeah,year,yes,yet,you,young,your,yourself,youth,"
        # Additional common words for better coverage
        "hello,hi,hey,bye,goodbye,please,sorry,thanks,thank,welcome,"
        "today,tomorrow,yesterday,morning,evening,afternoon,night,"
        "monday,tuesday,wednesday,thursday,friday,saturday,sunday,"
        "january,february,march,april,june,july,august,september,"
        "october,november,december,spring,summer,autumn,winter,"
        "red,blue,green,yellow,orange,purple,pink,brown,black,white,gray,grey,"
        "one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,"
        "thirteen,fourteen,fifteen,sixteen,seventeen,eighteen,nineteen,twenty,"
        "thirty,forty,fifty,sixty,seventy,eighty,ninety,hundred,thousand,"
        "million,billion,zero,first,second,third,fourth,fifth,"
        "i,me,my,mine,you,your,yours,he,him,his,she,her,hers,it,its,"
        "we,us,our,ours,they,them,their,theirs,who,whom,whose,"
        "this,that,these,those,what,which,where,when,how,why,"
        "am,is,are,was,were,been,being,have,has,had,having,"
        "do,does,did,doing,will,would,shall,should,can,could,may,might,"
        "must,need,dare,ought,used,go,goes,went,gone,going,"
        "get,gets,got,gotten,getting,make,makes,made,making,"
        "say,says,said,saying,know,knows,knew,known,knowing,"
        "think,thinks,thought,thinking,take,takes,took,taken,taking,"
        "see,sees,saw,seen,seeing,come,comes,came,coming,"
        "want,wants,wanted,wanting,give,gives,gave,given,giving,"
        "tell,tells,told,telling,work,works,worked,working,"
        "call,calls,called,calling,try,tries,tried,trying,"
        "ask,asks,asked,asking,use,uses,used,using,"
        "find,finds,found,finding,put,puts,putting,"
        "mean,means,meant,meaning,become,becomes,became,becoming,"
        "leave,leaves,leaving,keep,keeps,kept,keeping,"
        "let,lets,letting,begin,begins,began,begun,beginning,"
        "seem,seems,seemed,seeming,help,helps,helped,helping,"
        "show,shows,showed,shown,showing,hear,hears,heard,hearing,"
        "play,plays,played,playing,run,runs,ran,running,"
        "move,moves,moved,moving,live,lives,lived,living,"
        "believe,believes,believed,believing,bring,brings,brought,bringing,"
        "happen,happens,happened,happening,write,writes,wrote,written,writing,"
        "provide,provides,provided,providing,sit,sits,sat,sitting,"
        "stand,stands,stood,standing,lose,loses,lost,losing,"
        "pay,pays,paid,paying,meet,meets,met,meeting,"
        "include,includes,included,including,continue,continues,continued,continuing,"
        "set,sets,setting,learn,learns,learned,learning,"
        "change,changes,changed,changing,lead,leads,led,leading,"
        "understand,understands,understood,understanding,"
        "watch,watches,watched,watching,follow,follows,followed,following,"
        "stop,stops,stopped,stopping,create,creates,created,creating,"
        "speak,speaks,spoke,spoken,speaking,read,reads,reading,"
        "allow,allows,allowed,allowing,add,adds,added,adding,"
        "spend,spends,spent,spending,grow,grows,grew,grown,growing,"
        "open,opens,opened,opening,walk,walks,walked,walking,"
        "win,wins,won,winning,offer,offers,offered,offering,"
        "remember,remembers,remembered,remembering,"
        "love,loves,loved,loving,consider,considers,considered,considering,"
        "appear,appears,appeared,appearing,buy,buys,bought,buying,"
        "wait,waits,waited,waiting,serve,serves,served,serving,"
        "die,dies,died,dying,send,sends,sent,sending,"
        "expect,expects,expected,expecting,build,builds,built,building,"
        "stay,stays,stayed,staying,fall,falls,fell,fallen,falling,"
        "cut,cuts,cutting,reach,reaches,reached,reaching,"
        "kill,kills,killed,killing,remain,remains,remained,remaining,"
        "suggest,suggests,suggested,suggesting,raise,raises,raised,raising,"
        "pass,passes,passed,passing,sell,sells,sold,selling,"
        "require,requires,required,requiring,report,reports,reported,reporting,"
        "decide,decides,decided,deciding,pull,pulls,pulled,pulling,"
        "develop,develops,developed,developing,"
        "eat,eats,ate,eaten,eating,drink,drinks,drank,drunk,drinking,"
        "sleep,sleeps,slept,sleeping,sing,sings,sang,sung,singing,"
        "drive,drives,drove,driven,driving,draw,draws,drew,drawn,drawing,"
        "break,breaks,broke,broken,breaking,wear,wears,wore,worn,wearing,"
        "choose,chooses,chose,chosen,choosing,"
        "computer,software,hardware,internet,website,email,phone,"
        "application,program,system,data,information,technology,"
        "the,a,an,and,or,but,nor,for,yet,so,if,then,else,when,where,"
        "while,because,since,although,though,after,before,until,unless,"
        "spelling,checker,correct,correction,grammar,analyze,analysis,"
        "compiler,token,lexer,parser,syntax,semantic,error,warning,"
        "text,sentence,paragraph,document,file,upload,input,output,"
        "english,language,dictionary,vocabulary,definition,"
        # Animals
        "cat,dog,bird,fish,horse,cow,pig,sheep,chicken,duck,goat,rabbit,"
        "elephant,lion,tiger,bear,wolf,deer,mouse,rat,snake,frog,monkey,"
        "fox,bat,whale,shark,eagle,hawk,owl,penguin,zebra,giraffe,"
        "crocodile,alligator,turtle,butterfly,bee,ant,spider,mosquito,"
        # Common nouns
        "sample,example,people,person,thing,place,time,way,year,day,"
        "world,life,hand,part,number,water,words,money,story,point,"
        "fact,group,problem,answer,question,idea,plan,reason,power,"
        "need,house,home,room,door,window,floor,wall,roof,table,"
        "chair,desk,bed,kitchen,bathroom,garden,tree,flower,grass,"
        "river,lake,ocean,mountain,hill,valley,island,forest,field,"
        "road,street,bridge,town,village,market,shop,store,"
        "food,bread,rice,meat,fruit,apple,banana,milk,cheese,sugar,"
        "salt,butter,egg,soup,cake,coffee,tea,juice,wine,beer,"
        "clothes,shirt,dress,pants,shoes,hat,coat,jacket,skirt,"
        "body,face,eye,nose,ear,mouth,tooth,teeth,hair,neck,arm,"
        "leg,foot,feet,knee,hand,finger,thumb,heart,brain,bone,"
        "blood,skin,muscle,stomach,lung,shoulder,back,chest,hip,"
        "weather,rain,snow,cloud,storm,sun,moon,wind,sky,star,"
        "color,shape,circle,square,line,picture,music,song,"
        "book,page,letter,word,sentence,story,poem,lesson,"
        "class,student,teacher,school,college,university,test,exam,"
        "doctor,nurse,hospital,medicine,health,disease,pain,"
        "car,bus,train,plane,ship,boat,truck,bicycle,wheel,"
        "phone,computer,screen,camera,radio,television,machine,"
        "game,sport,ball,team,player,score,race,match,prize,"
        "king,queen,prince,princess,soldier,army,battle,war,peace,"
        # Common adjectives
        "big,small,large,little,long,short,tall,wide,narrow,thick,"
        "thin,heavy,light,fast,slow,hot,cold,warm,cool,new,old,"
        "young,good,bad,great,nice,fine,poor,rich,strong,weak,"
        "hard,soft,easy,difficult,simple,complex,clean,dirty,dry,wet,"
        "happy,sad,angry,afraid,brave,calm,quiet,loud,gentle,rough,"
        "bright,dark,deep,shallow,full,empty,open,close,high,low,"
        "right,wrong,true,false,real,fake,alive,dead,safe,dangerous,"
        "beautiful,ugly,pretty,handsome,smart,stupid,clever,wise,silly,"
        "funny,serious,strange,normal,special,usual,rare,common,"
        "important,useful,helpful,careful,wonderful,terrible,horrible,"
        "amazing,perfect,complete,ready,busy,lazy,tired,hungry,thirsty,"
        # Common adverbs
        "very,really,quite,pretty,too,also,just,still,already,yet,"
        "always,never,often,sometimes,usually,rarely,seldom,ever,"
        "here,there,everywhere,nowhere,somewhere,anywhere,"
        "now,then,soon,later,early,recently,today,yesterday,tomorrow,"
        "quickly,slowly,carefully,easily,hardly,nearly,almost,exactly,"
        "well,badly,fast,hard,far,near,close,together,apart,alone,"
        "away,back,forward,again,once,twice,also,either,neither,"
        # More verbs & past tenses
        "jump,jumps,jumped,jumping,look,looked,looking,looks,"
        "like,liked,likes,liking,need,needed,needs,needing,"
        "start,started,starts,starting,turn,turned,turns,turning,"
        "close,closed,closes,closing,feel,felt,feels,feeling,"
        "hold,held,holds,holding,carry,carried,carries,carrying,"
        "pick,picked,picks,picking,push,pushed,pushes,pushing,"
        "pull,pulled,pulls,pulling,touch,touched,touches,touching,"
        "throw,threw,throws,thrown,throwing,catch,caught,catches,catching,"
        "hit,hits,hitting,kick,kicked,kicks,kicking,"
        "smile,smiled,smiles,smiling,laugh,laughed,laughs,laughing,"
        "cry,cried,cries,crying,shout,shouted,shouts,shouting,"
        "talk,talked,talks,talking,listen,listened,listens,listening,"
        "answer,answered,answers,answering,explain,explained,explains,explaining,"
        "happen,happened,happens,fix,fixed,fixes,fixing,"
        "test,tested,tests,testing,check,checked,checks,checking,"
        "clean,cleaned,cleans,cleaning,cook,cooked,cooks,cooking,"
        "dance,danced,dances,dancing,paint,painted,paints,painting,"
        "swim,swam,swims,swum,swimming,climb,climbed,climbs,climbing,"
        "fly,flew,flown,flying,hang,hung,hangs,hanging,"
        "finish,finished,finishes,finishing,miss,missed,misses,missing,"
        "wake,woke,woken,wakes,waking,wish,wished,wishes,wishing,"
        "drop,dropped,drops,dropping,fill,filled,fills,filling,"
        "join,joined,joins,joining,cross,crossed,crosses,crossing,"
        "save,saved,saves,saving,spell,spelled,spells,spelling,"
        "correct,corrected,corrects,correcting,"
        # Common prepositions & conjunctions
        "about,above,across,after,against,along,among,around,"
        "at,before,behind,below,beneath,beside,between,beyond,"
        "by,down,during,except,for,from,in,inside,into,"
        "near,of,off,on,onto,out,outside,over,past,through,"
        "to,toward,towards,under,underneath,until,up,upon,with,"
        "within,without,and,but,or,nor,for,yet,so,because,"
        "since,although,though,while,if,unless,until,when,where,"
        # Plural forms & common endings
        "errors,words,things,people,children,women,men,days,years,"
        "times,ways,numbers,parts,places,cases,weeks,companies,"
        "groups,problems,facts,hands,months,points,rooms,areas,"
        "books,letters,girls,boys,students,teachers,friends,"
        "families,houses,countries,states,schools,stories,jobs,"
        "questions,answers,ideas,eyes,heads,sides,programs,"
        "games,lines,members,cities,names,results,changes,"
        "services,prices,cars,markets,forms,types,systems,"
        "plans,parties,lives,minutes,reasons,hours,parents,"
        "samples,examples,sentences,documents,paragraphs,files,"
        "papers,pages,pictures,windows,doors,tables,chairs"
    )
    # fmt: on
    return {w.strip().lower() for w in words.split(",") if w.strip()}


_COMMON_WORDS = _build_dictionary()


# ---------------------------------------------------------------------------
# Edit-distance helpers (Damerau-Levenshtein for suggestions)
# ---------------------------------------------------------------------------

def _edit_distance(a: str, b: str) -> int:
    """Compute the Damerau-Levenshtein distance between two strings."""
    len_a, len_b = len(a), len(b)
    d = [[0] * (len_b + 1) for _ in range(len_a + 1)]
    for i in range(len_a + 1):
        d[i][0] = i
    for j in range(len_b + 1):
        d[0][j] = j
    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,       # deletion
                d[i][j - 1] + 1,       # insertion
                d[i - 1][j - 1] + cost  # substitution
            )
            # transposition
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)
    return d[len_a][len_b]


def _suggest(word: str, max_suggestions: int = 5, max_distance: int = 2) -> List[str]:
    """Return up to *max_suggestions* dictionary words within *max_distance*
    edits of *word*, sorted by edit distance then alphabetically."""
    word_lower = word.lower()
    candidates: List[tuple] = []
    for dict_word in _COMMON_WORDS:
        # Quick length filter to avoid unnecessary computation
        if abs(len(dict_word) - len(word_lower)) > max_distance:
            continue
        dist = _edit_distance(word_lower, dict_word)
        if 0 < dist <= max_distance:
            candidates.append((dist, dict_word))
    candidates.sort()
    return [w for _, w in candidates[:max_suggestions]]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class SpellingError:
    word: str
    position: int
    line: int
    column: int
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "word": self.word,
            "position": self.position,
            "line": self.line,
            "column": self.column,
            "suggestions": self.suggestions,
        }


@dataclass
class SpellCheckResult:
    errors: List[SpellingError] = field(default_factory=list)
    corrected_text: str = ""
    total_words: int = 0
    misspelled_count: int = 0

    def to_dict(self):
        return {
            "errors": [e.to_dict() for e in self.errors],
            "corrected_text": self.corrected_text,
            "total_words": self.total_words,
            "misspelled_count": self.misspelled_count,
        }


def check_spelling(tokens: list, original_text: str) -> SpellCheckResult:
    """Validate spelling for every WORD token.  Returns a SpellCheckResult."""
    result = SpellCheckResult()
    corrections: Dict[int, str] = {}  # position -> replacement

    word_tokens = [t for t in tokens if t.type == TokenType.WORD]
    result.total_words = len(word_tokens)

    for token in word_tokens:
        word = token.value
        # Skip single characters, all-caps acronyms, and words with apostrophes
        if len(word) <= 1:
            continue
        if word.isupper() and len(word) <= 5:
            continue

        if word.lower() not in _COMMON_WORDS:
            suggestions = _suggest(word)
            error = SpellingError(
                word=word,
                position=token.position,
                line=token.line,
                column=token.column,
                suggestions=suggestions,
            )
            result.errors.append(error)
            result.misspelled_count += 1

            # Auto-correct with first suggestion if available
            if suggestions:
                # Preserve original casing pattern
                replacement = suggestions[0]
                if word[0].isupper():
                    replacement = replacement.capitalize()
                if word.isupper():
                    replacement = replacement.upper()
                corrections[token.position] = replacement

    # Build corrected text
    corrected = list(original_text)
    # Apply corrections in reverse order so positions stay valid
    for pos in sorted(corrections.keys(), reverse=True):
        orig_token = next(t for t in tokens if t.position == pos)
        orig_len = len(orig_token.value)
        corrected[pos: pos + orig_len] = list(corrections[pos])

    result.corrected_text = "".join(corrected)
    return result
