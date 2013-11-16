window.App = Ember.Application.create({
	LOG_TRANSITIONS: true
});

App.ApplicationAdapter = DS.FixtureAdapter.extend();

App.Router.map(function () {
  this.resource('libre', { path: '/' }, function(){
	  this.resource("message", { path: "/message/:message_id" });
  });
});

App.Message = DS.Model.extend({
  content1: DS.attr('string'),
  author: DS.attr('string'),
  date: DS.attr('date'),
  
  formatedDate: function() {
    return this.get('date').toLocaleString();
  }.property('date')
});

App.Message.FIXTURES = [
   {
     id: 1,
     content1: 'Tennessee Pastor Disputes Wildlife Possession Charge by State http://nyti.ms/1eXMq9H ',
     author: 'The New York Times',
     date: new Date('2013-01-01')
   },
   {
     id: 2,
     content1: "Il s'en est passé des choses cette semaine sur @franceinter ! Quoi ?... Réponse sur http://bit.ly/rambo72  #rambobino pic.twitter.com/kxHx4oaOIm",
     author: "France Inter",
     date: new Date('2013-01-01')
   },
   {
     id: 3,
     content1: "Bon, fin de l'analyse politique de comptoir, je vais aller chercher le pain.!",
     author: "Padre Pio",
     date: new Date('2013-01-01')
   }
  ];

App.LibreRoute = Ember.Route.extend({
  model: function () {
    return this.store.find('message');
  }
});

App.LibreIndexRoute = Ember.Route.extend({
  model: function () {
    return this.modelFor('libre');
  }
});

App.LibreController = Ember.ArrayController.extend({
	sortProperties: ['id'],
	sortAscending: false,
	actions: {
	    createMessage: function () {
	      var content1 = this.get('newMessage');
	      if (!content1.trim()) { return; }

	      var message = this.store.createRecord('message', {
	    	id: 4,
	        content1: content1,
	        author: 'me',
	        date: new Date()
	      });
	      this.set('newMessage', '');
	      message.save();
	    }
	}
});
