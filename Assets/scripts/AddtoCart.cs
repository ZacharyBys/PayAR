using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class AddtoCart : MonoBehaviour
{
    public TextMeshProUGUI infoText;
    // Start is called before the first frame update
    void Start()
    {
      
    }

   public void UpdateText()
    {
        infoText.text = "Testing Add";
    }
    // Update is called once per frame
    void Update()
    {
        
    }
}