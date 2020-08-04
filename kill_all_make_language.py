ps aux | grep -ie make_language | awk '{print $2}' | xargs kill -9 
