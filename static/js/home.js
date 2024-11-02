function handleCompetitionChange(competitionId) {
    // Handle voting section
    showCompetitionVote(competitionId);
    
    // Handle fixtures section
    showCompetitionFixtures(competitionId);
  
    // Handle results section
    showLatestResults(competitionId);
    
    // Handle standings section
    showCompetitionStandings(competitionId);
  
    // Handle awards section
    showCompetitionAward(competitionId);
  }
  