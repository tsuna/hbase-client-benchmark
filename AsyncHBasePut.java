/* Copyright 2010  Benoit Sigoure
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.  */
import org.hbase.async.HBaseClient;
import org.hbase.async.PutRequest;

final class AsyncHBasePut {
  public static void main(String[] a) throws Exception {
    final HBaseClient client = HBaseClientFactory.get();
    final PutRequest put = new PutRequest("hbench", "bar", "t",
					  "qualifier", "value");
    put.setBufferable(false);
    client.put(put);
    client.shutdown().join();
  }
}
