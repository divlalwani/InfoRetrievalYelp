//***************************************************************************************
//	Modified by Jayagowri on 12/7/2014.
//	Note: Input text should have words in the form - word#pos where pos 
//		  is the part of speech - a for adjective, v for verb, n for noun, r for adverb
//***************************************************************************************
//    Copyright 2013 Petter Tornberg
//
//    This demo code has been kindly provided by Petter Tornberg <pettert@chalmers.se>
//    for the SentiWordNet website.
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class SentiWordNetDemoCode {

    private Map<String, Double> dictionary;
    public static HashMap<String, HashMap<Integer, Double>> tempDictionary = new HashMap<String, HashMap<Integer, Double>>();

    public SentiWordNetDemoCode(String pathToSWN) throws IOException {
        // This is our main dictionary representation
        dictionary = new HashMap<String, Double>();

        BufferedReader csv = null;
        try {
            csv = new BufferedReader(new FileReader(pathToSWN));
            int lineNumber = 0;

            String line;
            while ((line = csv.readLine()) != null) {
                lineNumber++;

                // If it's a comment, skip this line.
                if (!line.trim().startsWith("#")) {
                    // We use tab separation
                    String[] data = line.split("\t");
                    String wordTypeMarker = data[0];

                    // Example line:
                    // POS ID PosS NegS SynsetTerm#sensenumber Desc
                    // a 00009618 0.5 0.25 spartan#4 austere#3 ascetical#2
                    // ascetic#2 practicing great self-denial;...etc

                    // Is it a valid line? Otherwise, through exception.
                    if (data.length != 6) {
                        throw new IllegalArgumentException(
                                "Incorrect tabulation format in file, line: "
                                        + lineNumber);
                    }

                    // Calculate synset score as score = PosS - NegS
                    Double synsetScore = Double.parseDouble(data[2])
                            - Double.parseDouble(data[3]);

                    // Get all Synset terms
                    String[] synTermsSplit = data[4].split(" ");

                    // Go through all terms of current synset.
                    for (String synTermSplit : synTermsSplit) {
                        // Get synterm and synterm rank
                        String[] synTermAndRank = synTermSplit.split("#");
                        String synTerm = synTermAndRank[0] + "#"
                                + wordTypeMarker;

                        int synTermRank = Integer.parseInt(synTermAndRank[1]);
                        // What we get here is a map of the type:
                        // term -> {score of synset#1, score of synset#2...}

                        // Add map to term if it doesn't have one
                        if (!tempDictionary.containsKey(synTerm)) {
                            tempDictionary.put(synTerm,
                                    new HashMap<Integer, Double>());
                        }

                        // Add synset link to synterm
                        tempDictionary.get(synTerm).put(synTermRank,
                                synsetScore);
                    }
                }
            }

            // Go through all the terms.
            for (Map.Entry<String, HashMap<Integer, Double>> entry : tempDictionary
                    .entrySet()) {
                String word = entry.getKey();
                Map<Integer, Double> synSetScoreMap = entry.getValue();

                // Calculate weighted average. Weigh the synsets according to
                // their rank.
                // Score= 1/2*first + 1/3*second + 1/4*third ..... etc.
                // Sum = 1/1 + 1/2 + 1/3 ...
                double score = 0.0;
                double sum = 0.0;
                for (Map.Entry<Integer, Double> setScore : synSetScoreMap
                        .entrySet()) {
                    score += setScore.getValue() / (double) setScore.getKey();
                    sum += 1.0 / (double) setScore.getKey();
                }
                score /= sum;

                dictionary.put(word, score);
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (csv != null) {
                csv.close();
            }
        }
    }

//    public double extract(String word, String pos) {
//        return dictionary.get(word + "#" + pos);
//    }

    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("Usage: java SentiWordNetDemoCode <pathToSentiWordNetFile>");
            return;
        }
        byte[] fileArray;
        String sourcePath = "C:\\Users\\Jayagowri\\Desktop\\reviews_5000_pos.txt";
        File file = new File(sourcePath);
        String stringPath = file.getPath();
        Path path = Paths.get(stringPath);
        fileArray = Files.readAllBytes(path);
        String decodedFile = new String(fileArray);
        String[] splitFile = decodedFile.split("\n");
        FileWriter fw = new FileWriter("rating_5000.txt");
        ArrayList<Double> topScore = new ArrayList<Double>();
        System.out.println(splitFile.length);
        for (int i = 0; i < splitFile.length; i++) {
            try {
                String[] splitString = splitFile[i].split("\t", 3);
                String[] words = splitString[2].split(" ");
                double sumScore = 0;
                for (int j = 0; j < words.length; j++) {
                    if (tempDictionary.containsKey(words[j].trim())) {
                        HashMap<Integer, Double> hm = tempDictionary.get(words[j].trim());
                        for (Map.Entry<Integer, Double> m : hm.entrySet()) {
                            topScore.add(m.getValue());
                            break;
                        }
                    }
                }
                Collections.sort(topScore);
                Collections.reverse(topScore);
                for (int k = 0; k < topScore.size(); k++) {
                    if (k >= 20)
                        break;
                    sumScore = sumScore + topScore.get(k);
                }
                int rating;
                if ((sumScore / 20) >= 0.75)
                    rating = 5;
                else if ((sumScore / 20) >= 0.55)
                    rating = 4;
                else if ((sumScore / 20) >= 0.35)
                    rating = 3;
                else if ((sumScore / 20) >= 0.15)
                    rating = 2;
                else
                    rating = 1;
                topScore.clear();
                if (rating == Integer.parseInt(splitString[1]))
                    fw.write(sumScore / 20 + "\t" + rating + "\t" + splitString[1] + "\t" + "Match");
                else
                    fw.write(sumScore / 20 + "\t" + rating + "\t" + splitString[1] + "\t" + "Mismatch");
                fw.write("\n");
            } catch (Exception e) {
                System.out.println("Error occured at " + i + 1 + "\t" + e.getMessage());
            }

        }
        fw.close();
    }
}
