Conversation format :

<!ELEMENT category (#CDATA)> => not included (c'est quoi)?)
<!ELEMENT nb_messages (role)*> => supprimé, comme suggéré ?
<!ATTLIST role
	type CDATA #REQUIRED
	value CDATA #REQUIRED> => uh ?
<!ELEMENT analysis (#PCDATA)> => ignoré
<!ELEMENT participants (user)*> => supprimé, comme suggéré ?
all_messages => messages

Message format :

<!ELEMENT date (#PCDATA)> => pas datetime ? format de date commun
inReplyTo camel case, avant snake case ?
conversation id dans inReplyTo element ?
champs "to" dans une mailing list ? ignoré pour le moment
ici aussi, analysis ignoré

pour forum posts, signature concaténée au contenu

infos perdues : "modification", "author_id", "datetime", thread url, closed, sticky...

user peut etre mieux défini ? email, id etc.

============

"mediums": redondant si la conversation inclut les messages, chacun incluant leur médium
"nb_messages": supprimé car calculable en parcourant les messages (déjà indiqué dans "commentaires-LINA")
"category": à quoi est ce que ça correspond exactement ?
"roles": est ce que les rôles ne devraient pas être définis en dehors de l'objet "conversation" ? sinon arbitraire
"all_messages": renommé en "messages" pour cohérence

============

"mediums": redondant si la conversation inclut les messages, chacun incluant leur médium, et pourquoi "séparé par un blanc" plutôt que sous-éléments ?
"analysis": bizarre de le garder ici

============

"to": ne suffit pas, compliqué pour une mailing list par exemple, et "cc" et "bcc": ne seraient pas une forme de "to" ? exemple:

<recipients>
	<recipient rel="to" id="cd.jean@laposte.net" role="client" realname="JEAN Didier" username="Jeanot22" email="d.jean@laposte.net" description=""/>
	<recipient rel="to" id="a32" role="agent" realname="" username="" email="ubuntu-fr@lists.ubuntu.com" description=""/>
	<recipient rel="cc" id="a33" role="superviser" realname="" username="" email="ubuntu@lists.ubuntu.com" description=""/>
	<recipient rel="bcc" id="o11" role="other" realname="" username="consommateurAverti" email="collectif@bidon.fr" description=""/>
	<recipient rel="bcc" id="o13" role="other" realname="" username="consommateurVigilent" email="conso@secure.fr" description=""/>
</recipients>

pareil dans "from", "email" devrait avoir des sous-types ("from", "sender", "return-path", "reply-to"...)
exemple pour un mail :

<sender>
  <sender id="cd.jean@laposte.net" role="client" realname="JEAN Didier" username="Jeanot22" sender="d.jean@laposte.net" reply-to="contact@laposte.net" from="mailagent@botserver.io" description=""/>
</sender>

Sinon <content><body></body></content> ne gère pas le multipart, ce qui est standard pour les mails, mais peut être utile aussi pour les forums (pour séparer la signature du contenu par exemple)

Qu'est ce qu'on met quand on a pas d'infos sur les likes ou les views ? 0 ? On ne fait pas de distinction entre un message qui a eu 0 vues et un message pour lequel on ne connaît pas le nombre de vues ? il faudrait mettre ça dans une catégorie contenant des items facultatifs pour les infos non génériques (comme "private" aussi), et il en faudrait une aussi pour les conversations et les participants. Sinon on perd pas mal d'infos dans les cas où on les a, comme par exemple si un thread est épinglé, si un post a été modifié etc. Exemple :

<conversation>
    <misc>
    	<item name="sticky" type="boolean">false</item>
    	<item name="closed" type="boolean">true</item>
    </misc>
	<messages> 
    	<message>
    		<misc>
    			<item name="likes" type="integer">1</item>
    			<item name="views" type="integer">12</item>
    			<item name="last_modified" type="datetime">01-12-2014 15:22:17</item>
    		</misc>
			<sender>
			  <sender>
			  	<misc>
			  		<item name="posts" type="integer">151</item>
			  		<item name="registration_date" type="datetime">22-11-2014 21:04:55</item>
			  	</misc>
			  </sender>
			</sender>
    		...
    	</message>
    	...
    </messages>
	...
</conversation>