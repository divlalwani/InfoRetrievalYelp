//*********************************************************************************************
// Created By Jayagowri
// Note:	Download the package from StandfordNLP site and replace the demo file with this file.
//*********************************************************************************************
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.util.*;

public class StanfordCoreNlpDemo {

    public static void main(String[] args) throws IOException {

        byte[] fileArray;
        String sourcePath = "C:\\Users\\Jayagowri\\Desktop\\GowriReviews_5000.json";
        File file = new File(sourcePath);
        String stringPath = file.getPath();
        Path path = Paths.get(stringPath);
        fileArray = Files.readAllBytes(path);
        String decodedFile = new String(fileArray);
        String[] splitFile = decodedFile.split("\n");
        System.out.println(splitFile.length);

        FileWriter fw = new FileWriter("outPOS_4000.txt", true);
        PrintWriter out;
        if (args.length > 1) {
            out = new PrintWriter(args[1]);
        } else {
            out = new PrintWriter(System.out);
        }
        PrintWriter xmlOut = null;
        if (args.length > 2) {
            xmlOut = new PrintWriter(args[2]);
        }

        StanfordCoreNLP pipeline = new StanfordCoreNLP();
        Annotation annotation;
        String concatSentence = "";
        if (args.length > 0) {
            annotation = new Annotation(IOUtils.slurpFileNoExceptions(args[0]));
        } else {
            for (int i = 0; i < splitFile.length; i++) {
                if ((i == 100) || (i == 200) || (i == 300) || (i == 400))
                    System.out.println("Completed: " + i);
                try {
                    String[] splitString = splitFile[i].split("\t", 3);
                    annotation = new Annotation(splitString[2]);
                    pipeline.annotate(annotation);
                    List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
                    for (int j = 0; j < sentences.size(); j++) {
                        ArrayCoreMap sentence = (ArrayCoreMap) sentences.get(j);
                        for (CoreMap token : sentence.get(CoreAnnotations.TokensAnnotation.class)) {
                            ArrayCoreMap aToken = (ArrayCoreMap) token;
                            String POS = aToken.toShorterString("PartOfSpeech");
                            String splitPOS[] = POS.split("PartOfSpeech=");
                            String word = splitPOS[1].substring(0, splitPOS[1].length() - 1);
                            if (word.equals("RB") || word.equals("RBR") || word.equals("RBS") || word.equals("LS") || word.equals("WRB"))
                                word = "r";
                            else if (word.equals("VB") || word.equals("VBD") || word.equals("VBG") || word.equals("VBN") || word.equals("VBP") || word.equals("VBZ") || word.equals("UH"))
                                word = "v";
                            else if (word.equals("NN") || word.equals("NNS") || word.equals("NNP") || word.equals("NNPS") || word.equals("PRP") || word.equals("PRP$") || word.equals("WP$") || word.equals("WP"))
                                word = "n";
                            else if (word.equals("JJ") || word.equals("JJR") || word.equals("JJS"))
                                word = "a";
                            else
                                continue;
                            concatSentence += aToken.toString().substring(0, aToken.toString().lastIndexOf("-")) + "#" + word + " ";
                        }
                    }
                    fw.write(splitString[0] + "\t" + splitString[1] + "\t" + concatSentence);
                    concatSentence = "";
                    fw.write("\n");
                } catch (Exception e) {
                    System.out.println("Error at Line: " + i + 1);
                }
            }
            fw.close();
        }
    }

}
