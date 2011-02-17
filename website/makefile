DIRS= cgi-bin etc web

all: 
	@for dir in $(DIRS); do \
	    ( cd $$dir && $(MAKE) all ) \
	done

install:
	@for dir in $(DIRS); do \
	    ( cd $$dir && $(MAKE) install ) \
	done

diff-install:
	@for dir in $(DIRS); do \
	    ( cd $$dir && $(MAKE) diff-install ) \
	done

test-install:
	@for dir in $(DIRS); do \
	    ( cd $$dir && $(MAKE) test-install ) \
	done

clean:
	@for dir in $(DIRS); do \
	    ( cd $$dir && $(MAKE) clean ) \
	done
