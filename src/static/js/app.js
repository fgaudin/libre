window.App = Ember.Application.create();
App.ApplicationAdapter = DS.FixtureAdapter.extend();

App.Router.map(function () {
  this.resource('messages', { path: '/' });
});

App.Message = DS.Model.extend({
  content: DS.attr('string'),
  author: DS.attr('string')
});

App.Message.FIXTURES = [
   {
     id: 1,
     content: 'Tennessee Pastor Disputes Wildlife Possession Charge by State http://nyti.ms/1eXMq9H ',
     author: 'The New York Times'
   },
   {
     id: 2,
     content: "Il s'en est passé des choses cette semaine sur @franceinter ! Quoi ?... Réponse sur http://bit.ly/rambo72  #rambobino pic.twitter.com/kxHx4oaOIm",
     author: "France Inter"
   },
   {
     id: 3,
     content: "Bon, fin de l'analyse politique de comptoir, je vais aller chercher le pain.!",
     author: "Padre Pio"
   }
  ];

App.MessagesRoute = Ember.Route.extend({
  model: function () {
    return this.store.find('message');
  }
});

App.MessagesController = Ember.ArrayController.extend({
	sortProperties: ['id'],
	sortAscending: false,
	actions: {
	    createMessage: function () {
	      var content = this.get('newMessage');
	      if (!content.trim()) { return; }

	      var message = this.store.createRecord('message', {
	    	id: 4,
	        content: content,
	        author: 'me'
	      });

	      // Clear the "New Todo" text field
	      this.set('newMessage', '');

	      // Save the new model
	      message.save();
	    }
	  }
	});