using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using TMPro;
using System.IO;
public class Checkout : VuforiaMonoBehaviour
{
[System.Serializable]
public class CheckoutResponse
{
    public string message;
}
[System.Serializable]
public class Response 
{
    public Cart cart;
}
[System.Serializable]
public class Cart
{
    public int id;
    public List<Item> items;
    public double total;
}
[System.Serializable]
public class Item
{  
    public Product product;
    public int quantity;
}
[System.Serializable]
public class Product
{
    public int id;
    public string name;
    public float price;
    public float inventory_count;
    public string description;
}

    // Start is called before the first frame update
    void Start()
    {
    }
    void Update() {
        if (Input.GetKeyDown("space"))
        {
            UpdateText();
        }
    }

    //string jsonResponse = "{\"cart\":{\"id\": 5, \"items\": [{\"product\": {\"id\": 1, \"name\": \"CSE Mints\", \"price\": 3.99, \"inventory_count\": 67, \"description\": \"Peppermint\"}, \"quantity\": 1}, {\"product\": {\"id\": 3, \"name\": \"MLH Hardware Sticker\", \"price\": 10.99, \"inventory_count\": 18, \"description\": \"Presented by Digi-Key\"}, \"quantity\": 2}], \"total\": 25.97}}";
    public void UpdateText() {
        int id = 5;
        //int id = this.transform.parent.parent.parent.parent.GetComponent<cartId>().cId;
         HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://dc3e9063.ngrok.io/carts/"+id);
        request.Method = "GET";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd(); 
        Response parsedResponse = JsonUtility.FromJson<Response>(jsonResponse);
        string Carttext = "";

        for (int i=0; i<parsedResponse.cart.items.Count; ++i) 
        {
            Carttext += parsedResponse.cart.items[i].product.name + "\n $" + parsedResponse.cart.items[i].product.price + "\t x" + parsedResponse.cart.items[i].quantity +"\n";
        }

        Carttext += "\n--------------------------\n";
        Carttext += "Your total: $" + parsedResponse.cart.total;
        this.transform.GetComponent<TextMeshProUGUI>().text = Carttext;
    }


    public void CompleteCheckout() 
    {
        //int id = this.transform.parent.parent.parent.parent.GetComponent<cartId>().cId;
        int id = 5;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://dc3e9063.ngrok.io/carts/" + id+"/checkout");
        request.Method = "POST";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        CheckoutResponse parsedResponse = JsonUtility.FromJson<CheckoutResponse>(jsonResponse);
        StartCoroutine(updateCheckout(parsedResponse.message));
    }

    IEnumerator updateCheckout(string parsedResponse) {
        this.transform.GetComponent<TextMeshProUGUI>().text = parsedResponse;
        yield return new WaitForSeconds(5);
        this.transform.GetComponent<TextMeshProUGUI>().text = "";
    }
}
